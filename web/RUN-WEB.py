# web/RUN-WEB.py
from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import os
import sys
import webbrowser  # [เพิ่ม] สำหรับเปิดเว็บใน Windows/PC
import time        # [เพิ่ม] สำหรับหน่วงเวลา

app = Flask(__name__)

# ตัวแปร Global สำหรับเก็บ Log
output_logs = []

# โฟลเดอร์ปัจจุบัน
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRAM_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "program"))

def get_script_path(mode):
    if mode == "fast":
        filename = "SMS-Fast.py"
    elif mode == "super":
        filename = "SMS-Super.py"
    else:
        filename = "SMS-Slow.py"
    return os.path.join(PROGRAM_DIR, filename)

def run_script(script_path, phone, count):
    global output_logs
    try:
        output_logs.clear()
        output_logs.append(f"[*] เริ่มรันไฟล์: {script_path}")
        output_logs.append(f"[*] เป้าหมายเบอร์: {phone}, จำนวน: {count}")

        process = subprocess.Popen(
            [sys.executable, "-u", script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            cwd=PROGRAM_DIR
        )

        try:
            input_str = f"{phone}\n{count}\n"
            process.stdin.write(input_str)
            process.stdin.flush()
        except Exception as e:
            output_logs.append(f"[!] Error sending input: {e}")

        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                output_logs.append(line.strip())

        stderr = process.stderr.read()
        if stderr:
            output_logs.append(f"[!] Error: {stderr}")

        output_logs.append("[*] ทำงานเสร็จสิ้น")

    except Exception as e:
        output_logs.append(f"[!] System Error: {e}")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run():
    data = request.json
    phone = data.get("phone")
    count = data.get("count")
    mode = data.get("mode")

    if not phone or not count:
        return jsonify({"status": "error", "message": "ต้องใส่ข้อมูลให้ครบ!"})

    script_path = get_script_path(mode)

    if not os.path.exists(script_path):
        return jsonify({"status": "error", "message": f"ไม่พบไฟล์ {script_path} \n(กรุณาเช็คว่ามีไฟล์ในโฟลเดอร์ program หรือยัง)"})

    threading.Thread(target=run_script, args=(script_path, phone, count)).start()

    return jsonify({"status": "success", "message": f"เริ่มรันโหมด {mode.upper()} แล้ว!"})

@app.route("/get_logs")
def get_logs():
    return jsonify(output_logs)

# [เพิ่ม] ฟังก์ชันเปิดเว็บอัตโนมัติ
def open_browser():
    url = "http://127.0.0.1:8080"
    
    # เช็คว่าเป็น Termux หรือไม่ (เช็คจากตัวแปร Environment ของ Android)
    if "ANDROID_ROOT" in os.environ:
        try:
            # คำสั่งสำหรับ Termux
            subprocess.run(["termux-open-url", url])
            print(f"[*] เปิดเว็บอัตโนมัติใน Termux: {url}")
        except FileNotFoundError:
            print("[!] ไม่พบคำสั่ง termux-open-url (ลองพิมพ์ pkg install termux-tools)")
    else:
        # สำหรับ Windows / macOS / Linux ทั่วไป
        webbrowser.open(url)
        print(f"[*] เปิดเว็บอัตโนมัติ: {url}")

if __name__ == "__main__":
    # ตั้งเวลาให้รันฟังก์ชัน open_browser หลังจาก Server เริ่มไปแล้ว 0.5 วินาที
    # ต้องใช้ Timer เพราะ app.run() มันจะบล็อกการทำงานบรรทัดต่อๆ ไป
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true': # ป้องกันการเปิดซ้ำเวลา Auto-reload ทำงาน
        threading.Timer(0.5, open_browser).start()
    
    app.run(host="0.0.0.0", port=8080, debug=True)
    
