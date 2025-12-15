import requests
import time
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent

# พยายาม import colorama เพื่อความสวยงาม ถ้าไม่มีให้ใช้ text ธรรมดา
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = CYAN = RESET = ""

ua = UserAgent()

# ==========================================
# CONFIGURATION & API FUNCTIONS
# ==========================================

def get_headers(referer, origin=None, content_type="application/json"):
    headers = {
        "User-Agent": ua.random,
        "Referer": referer
    }
    if origin:
        headers["Origin"] = origin
    if content_type:
        headers["Content-Type"] = content_type
    return headers

# รายการ API ทั้งหมดที่รวบรวมมาจากไฟล์ของคุณ
def test_api_1(phone):
    """Gogo-Shop"""
    url = "https://gogo-shop.com/app/index/send_sms"
    data = f"type=1&telephone={phone}&select=66"
    headers = get_headers("https://gogo-shop.com/", "https://gogo-shop.com", "application/x-www-form-urlencoded; charset=UTF-8")
    return requests.post(url, headers=headers, data=data, timeout=10)

def test_api_2(phone):
    """Kex-Express"""
    url = f"https://io.th.kex-express.com/firstmile-api/v3/keweb/otp/request/{phone}"
    headers = get_headers("https://th.kex-express.com/", "https://th.kex-express.com", "application/x-www-form-urlencoded")
    headers.update({"Appid": "Website_Api", "Appkey": "fcdf0569-c2a1-4dee-bd22-9d5361c047f2"})
    return requests.post(url, headers=headers, timeout=10)

def test_api_3(phone):
    """Jaomuehuay"""
    url = "https://jaomuehuay.io/api/auth/send-otp"
    payload = {"phone_number": phone, "affiliateCode": "jaomuehuay", "type": 1}
    headers = get_headers("https://jaomuehuay.io/", "https://jaomuehuay.io")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_4(phone):
    """Jut8"""
    url = "https://www.jut8.com/api/user/request-register-tac"
    payload = {"uname": "", "sendType": "mobile", "country_code": "66", "currency": "THB", "mobileno": phone, "language": "th", "langCountry": "th-th"}
    headers = get_headers("https://www.jut8.com/", "https://www.jut8.com")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_5(phone):
    """Cdo888"""
    url = "https://m.cdo888.bet/ajax/submitOTP"
    data = f"send_otp={phone}"
    headers = get_headers("https://m.cdo888.bet/", "https://m.cdo888.bet", "application/x-www-form-urlencoded; charset=UTF-8")
    return requests.post(url, headers=headers, data=data, timeout=10)

def test_api_6(phone):
    """Joneslot"""
    url = "https://www.joneslot.me/pussy888/otp.php?m=request"
    data = f"phone={phone}"
    headers = get_headers("https://www.joneslot.me/", "https://www.joneslot.me", "application/x-www-form-urlencoded; charset=UTF-8")
    return requests.post(url, headers=headers, data=data, timeout=10)

def test_api_7(phone):
    """Swin168"""
    url = "https://play.swin168.me/api/register/sms"
    payload = {"phone": phone, "agent_id": 1, "country_code": "TH"}
    headers = get_headers("https://play.swin168.me/", "https://play.swin168.me")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_8(phone):
    """Johnwick168"""
    url = "https://www.johnwick168.me/signup.php"
    data = f"act=step-1&tel={phone}"
    headers = get_headers("https://www.johnwick168.me/", "https://www.johnwick168.me", "application/x-www-form-urlencoded; charset=UTF-8")
    return requests.post(url, headers=headers, data=data, timeout=10)

def test_api_9(phone):
    """Skyslot7"""
    url = "https://skyslot7.me/member/otp.php?m=request"
    data = f"phone={phone}"
    headers = get_headers("https://skyslot7.me/", "https://skyslot7.me", "application/x-www-form-urlencoded; charset=UTF-8")
    return requests.post(url, headers=headers, data=data, timeout=10)

def test_api_10(phone):
    """Mgi88"""
    url = "https://mgi88.me/api/otp"
    payload = {"telefon_number": phone, "registrera_typ": ""}
    headers = get_headers("https://mgi88.me/", "https://mgi88.me")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_11(phone):
    """DeeCasino"""
    url = "https://play.dee.casino/api/register/sms"
    payload = {"phone": phone, "agent_id": 1, "country_code": "TH"}
    headers = get_headers("https://play.dee.casino/", "https://play.dee.casino")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_12(phone):
    """Mgame666"""
    url = "https://gw.mgame666.com/AuthAPI/SendSms"
    payload = {"Phone": phone}
    headers = get_headers("https://okmega.pgm77.com/", "https://okmega.pgm77.com")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_13(phone):
    """Prompkai"""
    url = "https://api.prompkai.com/auth/preRegister"
    payload = {"username": phone}
    headers = get_headers("https://www.prompkai.com/", "https://www.prompkai.com")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_14(phone):
    """Fun24"""
    url = "https://www.fun24.bet/_ajax_/v3/register/request-otp"
    data = f"phoneNumber={phone}"
    headers = get_headers("https://www.fun24.bet/", "https://www.fun24.bet", "application/x-www-form-urlencoded")
    return requests.post(url, headers=headers, data=data, timeout=10)

def test_api_15(phone):
    """Wm78bet"""
    url = "https://wm78bet.bet/_ajax_/v3/register/request-otp"
    data = f"phoneNumber={phone}"
    headers = get_headers("https://wm78bet.bet/", "https://wm78bet.bet", "application/x-www-form-urlencoded")
    return requests.post(url, headers=headers, data=data, timeout=10)

def test_api_16(phone):
    """Happy168"""
    url = "https://m.happy168.xyz/api/otp"
    payload = {"phone_number": phone, "register_type": ""}
    headers = get_headers("https://m.happy168.xyz/", "https://m.happy168.xyz")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_17(phone):
    """Pgheng"""
    url = "https://pgheng.amaheng.com/api/otp?lang=th"
    payload = {"phone_number": phone, "register_type": "", "type_otp": "register"}
    headers = get_headers("https://pgheng.amaheng.com/", "https://pgheng.amaheng.com")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_18(phone):
    """Aplusfun"""
    url = "https://www.aplusfun.bet/_ajax_/v3/register/request-otp"
    data = f"phoneNumber={phone}"
    headers = get_headers("https://www.aplusfun.bet/", "https://www.aplusfun.bet", "application/x-www-form-urlencoded")
    return requests.post(url, headers=headers, data=data, timeout=10)

def test_api_20(phone):
    """Oneforbet"""
    url = "https://api.oneforbet.com/auth/player/phone-check"
    payload = {"phone_number": phone}
    headers = get_headers("https://ohana888.net/", "https://ohana888.net", "application/json; charset=UTF-8")
    headers.update({"X-Site-Id": "26336fef-e961-449c-926d-93db6afef9c4", "X-Agency-Id": "df87f52d-4221-49b6-b6cb-827f92244b72"})
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_21(phone):
    """Joker123ths"""
    url = "https://m.joker123ths.shop/api/otp"
    payload = {"phone_number": phone, "register_type": ""}
    headers = get_headers("https://m.joker123ths.shop/", "https://m.joker123ths.shop")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_22(phone):
    """Jklmn23456 (Pigspin)"""
    url = "https://jklmn23456.com/api/v1/user/phone/verify"
    payload = {"phone_number": phone}
    headers = get_headers("https://pigspin.org/", "https://pigspin.org")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_23(phone):
    """i828th"""
    url = "https://www.i828th.com/api/user/request-register-tac"
    if phone.startswith("0"): p_clean = phone[1:]
    else: p_clean = phone
    payload = {"uname": f"66{p_clean}", "sendType": "mobile", "country_code": "66", "currency": "THB", "mobileno": p_clean, "language": "th", "langCountry": "th-th"}
    headers = get_headers("https://www.i828th.com/th-th?signup=1", "https://www.i828th.com")
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_24(phone):
    """Thai191"""
    url = "https://www.thai191.com/api/user/request-register-tac"
    if phone.startswith("0"): p_clean = phone[1:]
    else: p_clean = phone
    payload = {"sendType": "mobile", "currency": "THB", "country_code": "66", "mobileno": p_clean, "language": "th", "langCountry": "th-th"}
    headers = get_headers("https://www.thai191.com", None)
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_25(phone):
    """Pgs42s"""
    url = "https://pgs42s.online/api/otp?lang=th"
    payload = {"phone_number": phone, "register_type": "", "type_otp": "register"}
    headers = get_headers(None, None)
    return requests.post(url, headers=headers, json=payload, timeout=10)

def test_api_26(phone):
    """PgSlotIn"""
    url = "https://pgsoft.pgslotin.app/api/otp"
    payload = {"phone_number": phone, "register_type": ""}
    headers = get_headers("https://pgsoft.pgslotin.app/", "https://pgsoft.pgslotin.app")
    return requests.post(url, headers=headers, json=payload, timeout=10)

# รวม API เข้า List
API_LIST = [
    (test_api_1, "Gogo-Shop"), (test_api_2, "Kex-Express"), (test_api_3, "Jaomuehuay"),
    (test_api_4, "Jut8"), (test_api_5, "Cdo888"), (test_api_6, "Joneslot"),
    (test_api_7, "Swin168"), (test_api_8, "Johnwick168"), (test_api_9, "Skyslot7"),
    (test_api_10, "Mgi88"), (test_api_11, "DeeCasino"), (test_api_12, "Mgame666"),
    (test_api_13, "Prompkai"), (test_api_14, "Fun24"), (test_api_15, "Wm78bet"),
    (test_api_16, "Happy168"), (test_api_17, "Pgheng"), (test_api_18, "Aplusfun"),
    (test_api_20, "Oneforbet"), (test_api_21, "Joker123ths"), (test_api_22, "Pigspin"),
    (test_api_23, "i828th"), (test_api_24, "Thai191"), (test_api_25, "Pgs42s"),
    (test_api_26, "PgSlotIn")
]

# ==========================================
# CORE LOGIC
# ==========================================

def clean_phone(phone):
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("66"): return "0" + phone[2:]
    if phone.startswith("+66"): return "0" + phone[3:]
    return phone

def run_test(api_func, name, phone):
    start = time.time()
    try:
        response = api_func(phone)
        latency = (time.time() - start) * 1000
        status = response.status_code
        
        # เงื่อนไขความสำเร็จแบบกว้าง
        is_success = False
        if status in [200, 201]:
            txt = response.text.lower()
            if any(x in txt for x in ['success', 'true', 'code":200', 'code":1', '"ok"']):
                is_success = True
            elif len(txt) < 500: # ถ้า response สั้นๆ มักจะใช่
                 is_success = True

        if is_success:
            print(f"{GREEN}[PASS]{RESET} {name:<15} | Ping: {latency:.0f}ms | Status: {status}")
            return True
        else:
            print(f"{RED}[FAIL]{RESET} {name:<15} | Ping: {latency:.0f}ms | Status: {status}")
            return False

    except Exception as e:
        print(f"{RED}[ERR ]{RESET} {name:<15} | Msg: {str(e)[:30]}")
        return False

def main():
    print(f"{CYAN}========================================{RESET}")
    print(f"{CYAN}       SMS API DIAGNOSTIC TOOL          {RESET}")
    print(f"{CYAN}       By: Ninja System                 {RESET}")
    print(f"{CYAN}========================================{RESET}")
    
    phone = input(f"{YELLOW}ใส่เบอร์โทรศัพท์เพื่อทดสอบ: {RESET}")
    phone = clean_phone(phone)
    
    if len(phone) != 10:
        print(f"{RED}เบอร์โทรไม่ถูกต้อง!{RESET}")
        return

    print(f"\n{YELLOW}[*] กำลังเริ่มทดสอบ {len(API_LIST)} APIs...{RESET}\n")

    active_count = 0
    dead_count = 0

    # ใช้ ThreadPool เพื่อความเร็วในการทดสอบ
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for func, name in API_LIST:
            futures.append(executor.submit(run_test, func, name, phone))
        
        for future in futures:
            if future.result():
                active_count += 1
            else:
                dead_count += 1

    print(f"\n{CYAN}========================================{RESET}")
    print(f"ผลการทดสอบ:")
    print(f"{GREEN}ใช้งานได้ (Active): {active_count}{RESET}")
    print(f"{RED}ใช้งานไม่ได้ (Dead): {dead_count}{RESET}")
    print(f"{CYAN}========================================{RESET}")

if __name__ == "__main__":
    main()
