import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from API_LIST import API_CONFIG

# =========================
# Color (optional)
# =========================
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = CYAN = MAGENTA = RESET = ""

# =========================
# Utils
# =========================
def clean_phone(phone: str) -> str:
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("+66"):
        return "0" + phone[3:]
    if phone.startswith("66"):
        return "0" + phone[2:]
    return phone

# =========================
# Response Classifier
# =========================
def classify_response(status: int, text: str) -> str:
    t = (text or "").lower()

    # Success
    if status in (200, 201):
        if any(k in t for k in ["otp", "success", "sent", "ส่งแล้ว"]):
            return "PASS"
        if any(k in t for k in ["limit", "too many", "rate"]):
            return "RATE_LIMIT"
        if any(k in t for k in ["block", "forbidden", "denied"]):
            return "BLOCKED"
        return "SOFT_BLOCK"   # 200 แต่ไม่ส่งจริง

    # Client errors
    if status == 429:
        return "RATE_LIMIT"
    if status in (401, 403):
        return "BLOCKED"
    if status in (404, 405):
        return "ENDPOINT"

    # Server errors
    if status >= 500:
        return "SERVER"

    return "UNKNOWN"

# =========================
# Single API Test
# =========================
def run_test(api_data: dict, phone: str) -> dict:
    name = api_data["name"]
    start = time.time()

    url = api_data["url"].format(phone=phone) if "{phone}" in api_data["url"] else api_data["url"]
    headers = api_data["headers"]() if api_data.get("headers") else {}
    payload = api_data["data"](phone) if api_data.get("data") else None

    try:
        kwargs = {
            "headers": headers,
            "timeout": 10
        }
        if isinstance(payload, dict):
            kwargs["json"] = payload
        elif isinstance(payload, str):
            kwargs["data"] = payload

        resp = requests.request(api_data["method"], url, **kwargs)
        latency = int((time.time() - start) * 1000)

        result = classify_response(resp.status_code, resp.text)

        return {
            "name": name,
            "status": resp.status_code,
            "latency": latency,
            "result": result
        }

    except requests.exceptions.RequestException as e:
        return {
            "name": name,
            "status": None,
            "latency": None,
            "result": "NETWORK",
            "error": str(e)[:40]
        }

# =========================
# Pretty Print
# =========================
def print_result(r: dict):
    color = {
        "PASS": GREEN,
        "RATE_LIMIT": YELLOW,
        "BLOCKED": RED,
        "SOFT_BLOCK": MAGENTA,
        "ENDPOINT": CYAN,
        "SERVER": RED,
        "NETWORK": RED,
        "UNKNOWN": MAGENTA
    }.get(r["result"], "")

    status = r["status"] if r["status"] is not None else "--"
    ping = f"{r['latency']}ms" if r["latency"] is not None else "--"

    print(f"{color}[{r['result']:<10}]{RESET} {r['name']:<15} | Ping: {ping:<6} | Status: {status}")

# =========================
# Main
# =========================
def main():
    print(f"{CYAN}========================================{RESET}")
    print(f"{CYAN}       SMS API DIAGNOSTIC TOOL          {RESET}")
    print(f"{CYAN}       By: Ninja System                 {RESET}")
    print(f"{CYAN}========================================{RESET}")

    phone = clean_phone(input(f"{YELLOW}ใส่เบอร์โทรศัพท์เพื่อทดสอบ: {RESET}"))

    if len(phone) != 10:
        print(f"{RED}เบอร์โทรไม่ถูกต้อง!{RESET}")
        return

    print(f"\n{YELLOW}[*] กำลังเริ่มทดสอบ {len(API_CONFIG)} APIs...\n{RESET}")

    summary = {
        "PASS": 0,
        "RATE_LIMIT": 0,
        "BLOCKED": 0,
        "SOFT_BLOCK": 0,
        "ENDPOINT": 0,
        "SERVER": 0,
        "NETWORK": 0,
        "UNKNOWN": 0
    }

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(run_test, api, phone)
            for api in API_CONFIG.values()
        ]

        for future in as_completed(futures):
            r = future.result()
            print_result(r)
            summary[r["result"]] += 1

    print(f"\n{CYAN}========================================{RESET}")
    print("สรุปผลการทดสอบ:")
    for k, v in summary.items():
        if v:
            print(f"- {k:<10}: {v}")
    print(f"{CYAN}========================================{RESET}")

if __name__ == "__main__":
    main()
