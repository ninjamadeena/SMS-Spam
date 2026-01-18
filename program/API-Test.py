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
    try:
        obj = json.loads(text)
        return json.dumps(obj, indent=4, ensure_ascii=False)
    except:
        return text.strip()

# ==========================================
# 🧠 CORE LOGIC (SMARTER VERSION)
# ==========================================
def analyze_result(api_data, status, text):
    text_lower = text.lower()
    
    # 1. เช็คด้วย success_check จาก API_LIST ก่อน (แม่นยำที่สุด)
    if "success_check" in api_data and api_data["success_check"] is not None:
        try:
            if api_data["success_check"](text):
                return "PASS", C_GREEN
        except:
            pass # ถ้าเช็คแล้ว error ให้ข้ามไปเช็คแบบ generic

    # 2. เช็ค Status Code พื้นฐาน
    if status == 429: return "RATE LIMIT", C_YELLOW
    if status in (403, 401): return "BLOCKED IP", C_RED
    if status >= 500: return "SERVER ERR", C_RED
    if status == 405: return "METHOD ERR", C_RED

    # 3. Smart Generic Check (วิเคราะห์ข้อความตอบกลับแบบฉลาดขึ้น)
    
    # ถ้าเจอคำเหล่านี้ ให้ถือว่า Block ชัวร์ๆ
    if any(k in text_lower for k in ['cloudflare', 'bad gateway', 'service unavailable']):
        return "BLOCKED", C_RED

    # ถ้าเจอคำว่าเครดิตหมด/เงินไม่พอ
    if any(k in text_lower for k in ['insufficient', 'credit', 'balance', 'no money']):
        return "NO CREDIT", C_YELLOW

    # ถ้า response ว่างเปล่า หรือ []
    if text.strip() in ["[]", "{}"]:
        # บางเว็บถือว่าส่งแล้วแต่ไม่มี data กลับมา
        if status == 200: return "PASS (Empty)", C_GREEN
        return "EMPTY RESP", C_YELLOW

    # ถ้า Status 200 แต่เนื้อหาดูเหมือน Error
    # แต่ต้องระวัง! "error": false หรือ "code": 0 คือผ่าน
    is_json_success = False
    if '"error":false' in text.replace(" ", "") or '"code":0' in text.replace(" ", "") or '"status":"success"' in text:
        is_json_success = True

    if not is_json_success:
        if any(k in text_lower for k in ['error', 'fail', 'denied', 'not success', 'ref.3', 'wait', 'captcha', 'invalid']):
            return "SOFT BLOCK", C_YELLOW

    # สุดท้ายถ้า Status 200 และไม่เข้าข่าย Error ข้างบนเลย
    if status in (200, 201):
        return "PASS", C_GREEN
        
    return f"STATUS {status}", C_RED

def run_test_detailed(api_data, phone):
    name = api_data["name"]
    start = time.time()
    
    url = api_data["url"].format(phone=phone) if "{phone}" in api_data["url"] else api_data["url"]
    headers = api_data["headers"]() if api_data.get("headers") else {}
    payload_data = api_data["data"](phone) if api_data.get("data") else None
    
    try:
        kwargs = {"headers": headers, "timeout": 10} # เพิ่ม timeout นิดหน่อย
        if isinstance(payload_data, dict):
            kwargs["json"] = payload_data
            sent_type = "JSON"
        elif isinstance(payload_data, str):
            kwargs["data"] = payload_data
            sent_type = "DATA"
        else:
            sent_type = "NONE"

        resp = requests.request(api_data["method"], url, **kwargs)
        latency = int((time.time() - start) * 1000)
        
        # ใช้ Logic ใหม่ในการวิเคราะห์
        tag, color = analyze_result(api_data, resp.status_code, resp.text)
        
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
# 🖥️ DISPLAY
# ==========================================
def print_card(r):
    BORDER = f"{C_WHITE}" + "-"*65 + f"{C_RESET}"
    print(BORDER)
    print(f" {r['color']}● [{r['tag']:^12}] {C_CYAN}{r['name']:<20} {C_WHITE}({r['latency']}ms){C_RESET}")
    print(BORDER)
    
    if r['payload']:
        print(f" {C_BLUE}📤 SENT ({r['sent_type']}):{C_RESET}")
        payload_str = json.dumps(r['payload'], ensure_ascii=False) if isinstance(r['payload'], dict) else str(r['payload'])
        if len(payload_str) > 80: payload_str = payload_str[:80] + "..."
        print(f"    {C_WHITE}{payload_str}{C_RESET}")
        print(f"{C_WHITE}   . . . . . . . . . . . . . . . . . . . . . . . . . . . . .{C_RESET}")

    print(f" {C_MAGENTA}📥 RECEIVED:{C_RESET}")
    formatted_resp = "\n".join(["    " + line for line in r['response'].split('\n')])
    
    # สีของ Response ขึ้นอยู่กับสถานะ
    resp_color = C_GREEN if "PASS" in r['tag'] else C_WHITE
    print(f"{resp_color}{formatted_resp}{C_RESET}")
    print("\n")

def main():
    print(f"🔥 API TEST (Smart Mode) 🔥\n")
    phone = clean_phone(input(f"{C_YELLOW}🎯 Enter Target Phone: {C_RESET}"))
    if len(phone) != 10: return

    print(f"\n{C_WHITE}[*] Initializing scan on {len(API_CONFIG)} endpoints...{C_RESET}\n")

    summary = {"PASS": 0, "FAIL": 0, "WAIT": 0}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(run_test_detailed, api, phone) for api in API_CONFIG.values()]
        
        for future in as_completed(futures):
            r = future.result()
            print_card(r)
            
            # นับคะแนนสรุป (Logic นับแบบใหม่)
            if "PASS" in r['tag']: 
                summary["PASS"] += 1
            elif any(x in r['tag'] for x in ["LIMIT", "SOFT", "NO CREDIT"]): 
                summary["WAIT"] += 1
            else: 
                summary["FAIL"] += 1

    print(f"{C_CYAN}================================================================={C_RESET}")
    print(f"  🏁 SUMMARY REPORT")
    print(f"  {C_GREEN}✅ SUCCESS: {summary['PASS']}   {C_YELLOW}⚠️ WARNING: {summary['WAIT']}   {C_RED}❌ DEAD/BLOCK: {summary['FAIL']}{C_RESET}")
    print(f"{C_CYAN}================================================================={C_RESET}")

if __name__ == "__main__":
    main()
