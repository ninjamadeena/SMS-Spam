# program/API-Test.py
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from API-LIST import API_CONFIG # Import การตั้งค่ามา

# พยายาม import colorama เพื่อความสวยงาม
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

def clean_phone(phone):
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("66"): return "0" + phone[2:]
    if phone.startswith("+66"): return "0" + phone[3:]
    return phone

def run_test(api_key, api_data, phone):
    start = time.time()
    name = api_data["name"]
    
    # เตรียมข้อมูล
    url = api_data["url"].format(phone=phone) if "{phone}" in api_data["url"] else api_data["url"]
    headers = api_data["headers"]()
    data_input = api_data["data"](phone) if api_data["data"] else None
    
    try:
        kwargs = {"headers": headers, "timeout": 10}
        if isinstance(data_input, dict):
            kwargs["json"] = data_input
        elif isinstance(data_input, str):
            kwargs["data"] = data_input
        
        # ส่ง Request
        response = requests.request(api_data["method"], url, **kwargs)
        latency = (time.time() - start) * 1000
        
        # เช็คผลลัพธ์
        is_success = False
        if response.status_code in (200, 201):
            if api_data["success_check"](response.text):
                is_success = True
            elif len(response.text) < 500 and "error" not in response.text.lower():
                # Fallback check
                is_success = True

        if is_success:
            print(f"{GREEN}[PASS]{RESET} {name:<15} | Ping: {latency:.0f}ms | Status: {response.status_code}")
            return True
        else:
            print(f"{RED}[FAIL]{RESET} {name:<15} | Ping: {latency:.0f}ms | Status: {response.status_code}")
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

    print(f"\n{YELLOW}[*] กำลังเริ่มทดสอบ {len(API_CONFIG)} APIs...{RESET}\n")

    active_count = 0
    dead_count = 0

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        # วนลูป API ทั้งหมดจาก API_LIST
        for key, val in API_CONFIG.items():
            futures.append(executor.submit(run_test, key, val, phone))
        
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
