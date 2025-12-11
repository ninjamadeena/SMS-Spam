from flask import Flask, render_template, request, jsonify
import subprocess
import threading
import os
import sys

app = Flask(__name__)

# ตัวแปร Global สำหรับเก็บ Log
output_logs = []

# โฟลเดอร์ปัจจุบัน (ตำแหน่ง RUN-WEB.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# โฟลเดอร์ program ที่อยู่ระดับบน
PROGRAM_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "program"))

# ฟังก์ชันสร้าง path ของไฟล์ SMS
def get_script_path(mode):
    filename = "SMS-Fast.py" if mode == "fast" else "SMS-Slow.py"
    return os.path.join(PROGRAM_DIR, filename)


def run_script(script_path, phone, count):
    global output_logs
    try:
        output_logs.clear()
        output_logs.append(f"[*] เริ่มรันไฟล์: {script_path}")
        output_logs.append(f"[*] ส่งไปที่เบอร์: {phone}, จำนวน: {count}")

        # ใช้ python interpreter ตัวเดียวกับที่รัน Flask อยู่ (รองรับทุก OS)
        process = subprocess.Popen(
            [sys.executable, "-u", script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # ส่ง input เข้าไฟล์ Python
        try:
            process.stdin.write(f"{phone}\n{count}\n")
            process.stdin.flush()
        except Exception as e:
            output_logs.append(f"[!] Error sending input: {e}")

        # อ่าน output แบบ real-time
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                output_logs.append(line.strip())

        # อ่าน error ถ้ามี
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

    # หา path ของไฟล์ให้ถูกตามทุก OS
    script_path = get_script_path(mode)

    if not os.path.exists(script_path):
        return jsonify({"status": "error", "message": f"ไม่พบไฟล์ {script_path}"})

    threading.Thread(target=run_script, args=(script_path, phone, count)).start()

    return jsonify({"status": "success", "message": f"เริ่มรัน {script_path} แล้ว!"})


@app.route("/get_logs")
def get_logs():
    return jsonify(output_logs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
