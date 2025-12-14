import os
import shutil
import subprocess
import sys

# --- Configuration ---
REPO_URL = "https://github.com/ninjamadeena/SMS-Spam.git"
TEMP_DIR = "temp_update_folder"
# ระบุ path ของ root directory (ถอยออกมา 1 ชั้นจากโฟลเดอร์ program)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# สีสำหรับแสดงผล
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def print_msg(msg, color=Colors.ENDC):
    print(f"{color}{msg}{Colors.ENDC}")

def update_system():
    print_msg("\n🔄 กำลังเริ่มกระบวนการอัปเดต...", Colors.CYAN)
    
    # เปลี่ยน path การทำงานไปที่ Root โปรเจกต์เสมอ เพื่อความชัวร์
    os.chdir(ROOT_DIR)

    # 1. สร้างโฟลเดอร์ชั่วคราว
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    
    # 2. โคลนไฟล์ใหม่มา
    print_msg("[*] กำลังดาวน์โหลดไฟล์ล่าสุด...", Colors.YELLOW)
    try:
        subprocess.check_call(f"git clone {REPO_URL} {TEMP_DIR}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        print_msg("[!] ดาวน์โหลดไม่สำเร็จ เช็คเน็ตแล้วลองใหม่", Colors.RED)
        return

    # 3. รายการที่จะอัปเดต (เขียนทับ)
    items = ["program", "web", "requirements.txt", "SMS-RUN-WEB-TERMUX.sh"]
    
    print_msg("[*] กำลังเขียนทับไฟล์ระบบ...", Colors.YELLOW)
    for item in items:
        src = os.path.join(TEMP_DIR, item)
        dst = os.path.join(ROOT_DIR, item)
        
        if os.path.exists(src):
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"    - Updated: {item}")

    # 4. อัปเดตคำสั่งรัน (ย้ายไป bin)
    try:
        source_bin = "SMS-RUN-WEB-TERMUX.sh"
        target_bin = os.path.join(os.environ.get('PREFIX', '/usr'), 'bin', 'RUN-SMS-WEB')
        
        if os.path.exists(source_bin):
            shutil.copy2(source_bin, target_bin)
            os.chmod(target_bin, 0o755)
            print_msg("[*] อัปเดตคำสั่ง RUN-SMS-WEB เรียบร้อย", Colors.GREEN)
    except Exception as e:
        print_msg(f"[!] Warning: ไม่สามารถอัปเดตคำสั่งใน bin ได้ ({e})", Colors.RED)

    # 5. Cleanup
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        
    print_msg("\n✅ อัปเดตเสร็จสมบูรณ์! พร้อมใช้งาน", Colors.GREEN)

if __name__ == "__main__":
    update_system()
