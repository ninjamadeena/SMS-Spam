# -*- coding: utf-8 -*-
import os
import requests
import time
import json
import urllib3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from API_LIST import API_CONFIG

# ปิด Warning กรณีบางเว็บ SSL Certificate มีปัญหาแต่ต้องการทดสอบต่อ
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# โฟลเดอร์ที่ไฟล์สคริปต์นี้อยู่
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    except Exception:
        return text.strip()

# ==========================================
# 🧠 CORE LOGIC (ULTRA STRICT VERSION)
# ==========================================
def analyze_result(api_data, status, text):
    t_strip = (text or "").strip()
    t_low = t_strip.lower()
    t_nospace = t_low.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")

    # 1. ดัก WAF / Cloudflare / Security Block ก่อนเสมอ (แม้จะตอบ Status 200)
    if any(k in t_low for k in [
        "cloudflare", "attention required!", "just a moment...",
        "security check in progress", "byteplus", "aliyun.com",
        "edgesuite.net", "access denied", "blocked because of security"
    ]):
        return "WAF BLOCK", C_RED

    # 2. ดัก HTTP Status Code ที่ผิดพลาดชัดเจนก่อนเรียก success_check
    if status == 429 or "429 too many requests" in t_low or "maximum quota limit" in t_low:
        return "RATE LIMIT", C_YELLOW
    if status in (401, 403):
        return "BLOCKED IP", C_RED
    if status == 404:
        return "NOT FOUND", C_RED
    if status == 405 or "method not allowed" in t_low or "<title>405</title>" in t_low:
        return "METHOD ERR", C_RED
    if status == 400:
        return "BAD REQ", C_YELLOW
    if status >= 500 or "slim application error" in t_low or "__next_error__" in t_low:
        return "SERVER ERR", C_RED

    # 3. ดักหน้าเว็บ HTML แปลกปลอม / หน้า 404 ที่ตอบกลับด้วย Status 200
    if any(k in t_low for k in [
        "404 not found", "page not found", "404; not found", "404.html",
        "404 error", "โอ้ไม่ ไม่พบ", "invalid url", "no http resource was found",
        "api page not found", "persistedquerynotfound", "notfounderror"
    ]):
        return "DEAD API", C_RED

    if any(k in t_low for k in ["<!doctype", "<html", "<head", "<body"]):
        return "HTML RESP", C_RED

    # 4. ดัก Captcha / Token หมดอายุ / ขาดพารามิเตอร์
    if any(k in t_low for k in ["captcha", "recaptcha", "turnstile", "csrf token"]):
        return "CAPTCHA", C_YELLOW

    if any(k in t_low for k in ["insufficient", "credit", "balance", "no money"]):
        return "NO CREDIT", C_YELLOW

    # 5. ดัก Response ว่างเปล่า หรือ {"data": null}
    if not t_strip or t_strip in ["﻿", "{}", '{"data":null}'] or t_nospace == '{"data":null}':
        return "EMPTY/NULL", C_YELLOW

    # 6. เช็คด้วย success_check จาก API_LIST (หลังจากกรอง Error และ HTML ออกหมดแล้ว)
    has_custom_check = "success_check" in api_data and api_data["success_check"] is not None
    if has_custom_check:
        try:
            if api_data["success_check"](text):
                return "PASS", C_GREEN
            else:
                # ถ้ามี success_check แล้วคืนค่า False จะไม่ปล่อยผ่านเด็ดขาด!
                if any(k in t_low for k in [
                    "error", "fail", "denied", "invalid", "wrong", "missing",
                    "ไม่สำเร็จ", "ไม่สามารถ", "ไม่ถูกต้อง", "ไม่พบ", "ไม่มี", "upgrade"
                ]):
                    return "SOFT BLOCK", C_YELLOW
                return "UNVERIFIED", C_YELLOW
        except Exception:
            return "CHECK ERR", C_YELLOW

    # 7. Fallback กรณีไม่ได้กำหนด success_check ไว้ใน API_LIST
    if any(f in t_nospace for f in [
        '"error":true', '"success":false', '"issuccess":false', '"status":false'
    ]):
        return "SOFT BLOCK", C_YELLOW

    if status in (200, 201) and any(s in t_nospace for s in [
        '"status":"success"', '"success":true', '"issuccess":true', '"is_success":true',
        '"code":0', '"code":200', '"status":1', '"status":200'
    ]):
        return "PASS", C_GREEN

    return f"STATUS {status}", C_YELLOW

def run_test_detailed(api_data, phone):
    name = api_data["name"]
    start = time.time()
    phone_no_zero = phone[1:] if phone.startswith("0") else phone
    
    raw_url = api_data["url"]
    url = raw_url.format(phone=phone, phone_no_zero=phone_no_zero) if ("{phone" in raw_url) else raw_url
    headers = api_data["headers"]() if api_data.get("headers") else {}
    
    try:
        payload_data = api_data["data"](phone) if api_data.get("data") else None
    except Exception as e:
        return {
            "name": name,
            "latency": 0,
            "tag": "CONFIG ERR",
            "color": C_RED,
            "sent_type": "ERR",
            "payload": None,
            "response": f"Payload build error: {e}"
        }
    
    try:
        kwargs = {"headers": headers, "timeout": 10}
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
# 🖥️ DISPLAY & 📝 FILE LOGGING
# ==========================================
def print_card(r, max_lines=15, max_chars=500):
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
    
    resp_text = r['response']
    truncated = False
    if len(resp_text) > max_chars:
        resp_text = resp_text[:max_chars]
        truncated = True
        
    lines = resp_text.split('\n')
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        truncated = True

    formatted_resp = "\n".join(["    " + line for line in lines])
    
    resp_color = C_GREEN if r['tag'] == "PASS" else C_WHITE
    print(f"{resp_color}{formatted_resp}{C_RESET}")
    if truncated:
        print(f"    {C_YELLOW}... [ข้อความยาวเกินไป ดูฉบับเต็มได้ในไฟล์ .txt] ...{C_RESET}")
    print("\n")

def format_card_for_file(r):
    border = "-" * 65
    lines = [
        border,
        f" ● [{r['tag']:^12}] {r['name']:<20} ({r['latency']}ms)",
        border
    ]
    if r['payload']:
        payload_str = json.dumps(r['payload'], ensure_ascii=False, indent=4) if isinstance(r['payload'], dict) else str(r['payload'])
        formatted_payload = "\n".join(["    " + line for line in payload_str.split('\n')])
        lines.append(f" 📤 SENT ({r['sent_type']}):\n{formatted_payload}")
        lines.append("   . . . . . . . . . . . . . . . . . . . . . . . . . . . . .")

    formatted_resp = "\n".join(["    " + line for line in r['response'].split('\n')])
    lines.append(f" 📥 RECEIVED (FULL):\n{formatted_resp}\n\n")
    return "\n".join(lines)

def main():
    print(f"🔥 API TEST (Ultra Strict Mode) 🔥\n")
    phone = clean_phone(input(f"{C_YELLOW}🎯 Enter Target Phone: {C_RESET}"))
    if len(phone) != 10: return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"API-Test-Result-{timestamp}.txt"
    log_filepath = os.path.join(BASE_DIR, log_filename)

    print(f"\n{C_WHITE}[*] Initializing scan on {len(API_CONFIG)} endpoints...{C_RESET}")
    print(f"{C_WHITE}[*] Saving full results to: {log_filepath}{C_RESET}\n")

    summary = {"PASS": 0, "FAIL": 0, "WAIT": 0}
    passed_apis = []

    with open(log_filepath, "w", encoding="utf-8") as log_file:
        log_file.write("=================================================================\n")
        log_file.write(f" 🔥 API TEST REPORT (ULTRA STRICT) - {timestamp}\n")
        log_file.write(f" 🎯 Target Phone: {phone} | Total Endpoints: {len(API_CONFIG)}\n")
        log_file.write("=================================================================\n\n")

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_test_detailed, api, phone) for api in API_CONFIG.values()]
            
            for future in as_completed(futures):
                r = future.result()
                print_card(r)
                
                log_file.write(format_card_for_file(r))
                log_file.flush()
                
                if r['tag'] == "PASS": 
                    summary["PASS"] += 1
                    passed_apis.append(f"{r['name']} ({r['latency']}ms)")
                elif r['tag'] in ("RATE LIMIT", "SOFT BLOCK", "NO CREDIT", "CAPTCHA", "EMPTY/NULL", "UNVERIFIED", "BAD REQ"): 
                    summary["WAIT"] += 1
                else: 
                    summary["FAIL"] += 1

        passed_list_str = "\n".join([f"    - {name}" for name in passed_apis]) if passed_apis else "    - ไม่มี"
        summary_text = (
            "=================================================================\n"
            "  🏁 SUMMARY REPORT (ULTRA STRICT)\n"
            f"  ✅ REAL SUCCESS: {summary['PASS']}   ⚠️ SOFT BLOCK/LIMIT/EMPTY: {summary['WAIT']}   ❌ DEAD/WAF/ERR: {summary['FAIL']}\n"
            "-----------------------------------------------------------------\n"
            f"  🎯 รายชื่อ API ที่ส่งผ่านจริง ({len(passed_apis)} รายการ):\n"
            f"{passed_list_str}\n"
            "=================================================================\n"
        )
        log_file.write(summary_text)

    print(f"{C_CYAN}================================================================={C_RESET}")
    print(f"  🏁 SUMMARY REPORT (ULTRA STRICT)")
    print(f"  {C_GREEN}✅ REAL SUCCESS: {summary['PASS']}   {C_YELLOW}⚠️ SOFT BLOCK/LIMIT/EMPTY: {summary['WAIT']}   {C_RED}❌ DEAD/WAF/ERR: {summary['FAIL']}{C_RESET}")
    if passed_apis:
        print(f"  {C_GREEN}🎯 รายชื่อ API ที่ส่งผ่านจริง:{C_RESET}")
        for p_api in passed_apis:
            print(f"     {C_GREEN}• {p_api}{C_RESET}")
    print(f"  {C_CYAN}📄 บันทึกผลลัพธ์ฉบับเต็มไว้ที่: {C_WHITE}{log_filepath}{C_RESET}")
    print(f"{C_CYAN}================================================================={C_RESET}")

if __name__ == "__main__":
    main()
