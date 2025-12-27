# -*- coding: utf-8 -*-
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from API_LIST import API_CONFIG

# ==========================================
# 🎨 COLOR & STYLE SYSTEM
# ==========================================
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    C_GREEN = Fore.GREEN + Style.BRIGHT
    C_RED = Fore.RED + Style.BRIGHT
    C_YELLOW = Fore.YELLOW + Style.BRIGHT
    C_CYAN = Fore.CYAN + Style.BRIGHT
    C_BLUE = Fore.BLUE + Style.BRIGHT
    C_MAGENTA = Fore.MAGENTA + Style.BRIGHT
    C_WHITE = Fore.WHITE + Style.DIM
    C_RESET = Style.RESET_ALL
except ImportError:
    C_GREEN = C_RED = C_YELLOW = C_CYAN = C_BLUE = C_MAGENTA = C_WHITE = C_RESET = ""

# ==========================================
# 🛠️ UTILS
# ==========================================
def clean_phone(phone: str) -> str:
    phone = "".join(filter(str.isdigit, phone.strip()))
    if phone.startswith("+66"): return "0" + phone[3:]
    if phone.startswith("66"): return "0" + phone[2:]
    return phone

def format_json(text):
    """จัด Format JSON ให้สวยงาม อ่านง่าย"""
    try:
        obj = json.loads(text)
        return json.dumps(obj, indent=4, ensure_ascii=False)
    except:
        return text.strip()

# ==========================================
# 🧠 CORE LOGIC
# ==========================================
def analyze_status(status, text):
    text_lower = text.lower()
    
    if status in (200, 201):
        # 200 แต่เนื้อหาบอกว่า Error
        if any(k in text_lower for k in ['error', 'fail', 'denied', 'limit', 'not success', 'ref.3', 'wait']):
            return "SOFT BLOCK", C_YELLOW
        # 200 ปกติ
        if any(k in text_lower for k in ['success', 'true', 'sent', 'otp', 'code":200', 'code":1']):
            return "PASS", C_GREEN
        # กรณี Fun24 ตอบกลับมาเป็น [] ว่างๆ
        if text.strip() == "[]":
            return "PASS (Empty)", C_GREEN
        
        return "UNKNOWN 200", C_BLUE

    if status == 429: return "RATE LIMIT", C_YELLOW
    if status in (403, 401): return "BLOCKED IP", C_RED
    if status == 400: return "BAD REQUEST", C_RED
    if status == 404: return "NOT FOUND", C_WHITE
    if status >= 500: return "SERVER ERR", C_RED
    
    return f"STATUS {status}", C_RED

def run_test_detailed(api_data, phone):
    name = api_data["name"]
    start = time.time()
    
    # เตรียมข้อมูล (Capture Payload เพื่อแสดงผล)
    url = api_data["url"].format(phone=phone) if "{phone}" in api_data["url"] else api_data["url"]
    headers = api_data["headers"]() if api_data.get("headers") else {}
    payload_data = api_data["data"](phone) if api_data.get("data") else None
    
    try:
        kwargs = {"headers": headers, "timeout": 8}
        if isinstance(payload_data, dict):
            kwargs["json"] = payload_data
            sent_type = "JSON"
        elif isinstance(payload_data, str):
            kwargs["data"] = payload_data
            sent_type = "DATA"
        else:
            sent_type = "NONE"

        # ยิง !!!
        resp = requests.request(api_data["method"], url, **kwargs)
        latency = int((time.time() - start) * 1000)
        
        # วิเคราะห์ผล
        tag, color = analyze_status(resp.status_code, resp.text)
        
        return {
            "name": name,
            "latency": latency,
            "tag": tag,
            "color": color,
            "sent_type": sent_type,
            "payload": payload_data,
            "response": format_json(resp.text)
        }

    except Exception as e:
        return {
            "name": name,
            "latency": 0,
            "tag": "NETWORK ERR",
            "color": C_RED,
            "sent_type": "ERR",
            "payload": None,
            "response": str(e)
        }

# ==========================================
# 🖥️ DISPLAY (THE BEAUTIFUL PART)
# ==========================================
def print_card(r):
    # เส้นขอบ
    BORDER = f"{C_WHITE}" + "-"*65 + f"{C_RESET}"
    
    # Header ส่วนบน: [STATUS] API Name (Ping)
    print(BORDER)
    print(f" {r['color']}● [{r['tag']:^12}] {C_CYAN}{r['name']:<20} {C_WHITE}({r['latency']}ms){C_RESET}")
    print(BORDER)
    
    # ส่วน Payload (สิ่งที่เราส่งไป) - เฉพาะถ้ามีของส่งไป
    if r['payload']:
        print(f" {C_BLUE}📤 SENT ({r['sent_type']}):{C_RESET}")
        payload_str = json.dumps(r['payload'], ensure_ascii=False) if isinstance(r['payload'], dict) else str(r['payload'])
        # ตัดคำถ้าส่งยาวเกิน
        if len(payload_str) > 80: payload_str = payload_str[:80] + "..."
        print(f"    {C_WHITE}{payload_str}{C_RESET}")
        print(f"{C_WHITE}   . . . . . . . . . . . . . . . . . . . . . . . . . . . . .{C_RESET}")

    # ส่วน Response (สิ่งที่ตอบกลับมา) - หัวใจสำคัญ
    print(f" {C_MAGENTA}📥 RECEIVED:{C_RESET}")
    # Indent บรรทัดให้สวย
    formatted_resp = "\n".join(["    " + line for line in r['response'].split('\n')])
    print(f"{C_GREEN if 'PASS' in r['tag'] else C_WHITE}{formatted_resp}{C_RESET}")
    print("\n") # เว้นบรรทัดระหว่างการ์ด

def main():
    print(f"🔥 API TEST 🔥\n")
    phone = clean_phone(input(f"{C_YELLOW}🎯 Enter Target Phone: {C_RESET}"))
    if len(phone) != 10: return

    print(f"\n{C_WHITE}[*] Initializing scan on {len(API_CONFIG)} endpoints...{C_RESET}\n")

    summary = {"PASS": 0, "FAIL": 0, "WAIT": 0}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_test_detailed, api, phone) for api in API_CONFIG.values()]
        
        for future in as_completed(futures):
            r = future.result()
            print_card(r)
            
            # นับคะแนนสรุป
            if "PASS" in r['tag']: summary["PASS"] += 1
            elif "LIMIT" in r['tag'] or "SOFT" in r['tag']: summary["WAIT"] += 1
            else: summary["FAIL"] += 1

    print(f"{C_CYAN}================================================================={C_RESET}")
    print(f"  🏁 SUMMARY REPORT")
    print(f"  {C_GREEN}✅ SUCCESS: {summary['PASS']}   {C_YELLOW}⚠️ WARNING: {summary['WAIT']}   {C_RED}❌ DEAD/BLOCK: {summary['FAIL']}{C_RESET}")
    print(f"{C_CYAN}================================================================={C_RESET}")

if __name__ == "__main__":
    main()
