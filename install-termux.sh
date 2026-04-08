#!/data/data/com.termux/files/usr/bin/bash

echo "=== INSTALL SCRIPT FOR SMS-SPAM WEB ==="

# -----------------------------
# 1. ตรวจ Python
# -----------------------------
if ! command -v python >/dev/null 2>&1; then
    echo "[*] ไม่พบ Python -> กำลังติดตั้ง..."
    pkg update -y
    pkg install python -y
else
    echo "[OK] พบ Python แล้ว"
fi

# -----------------------------
# 2. ตรวจ pip
# -----------------------------
if ! command -v pip >/dev/null 2>&1; then
    echo "[*] ไม่พบ pip -> กำลังติดตั้ง..."
    # ปกติ pip มาพร้อม python แต่กันเหนียว
    pkg install python-pip -y 
else
    echo "[OK] พบ pip แล้ว"
fi

# -----------------------------
# 3. ติดตั้ง dependencies จาก requirements.txt
# -----------------------------
REQ_FILE="setup/requirements.txt"

if [ ! -f "$REQ_FILE" ]; then
    echo "[!] ไม่พบไฟล์ $REQ_FILE"
    exit 1
fi

echo "[*] กำลังติดตั้ง dependencies จาก $REQ_FILE..."
pip install -r "$REQ_FILE"

if [ $? -eq 0 ]; then
    echo "[OK] ติดตั้ง dependencies เรียบร้อย"
else
    echo "[!] เกิดข้อผิดพลาดในการติดตั้ง dependencies"
    exit 1
fi

# -----------------------------
# 4. ติดตั้งคำสั่ง RUN-SMS-WEB
# -----------------------------
TARGET="$PREFIX/bin/RUN-SMS-WEB"
SOURCE="setup/SMS-RUN-WEB-TERMUX.sh"

if [ ! -f "$SOURCE" ]; then
    echo "[!] ไม่พบไฟล์ $SOURCE สำหรับสร้างคำสั่งรัน"
    # ไม่ exit เพราะอาจจะแค่อยากลง library
else
    echo "[*] กำลังติดตั้งคำสั่ง RUN-SMS-WEB ..."
    mv "$SOURCE" "$TARGET"
    chmod +x "$TARGET"
    echo "[OK] ติดตั้งคำสั่ง RUN-SMS-WEB สำเร็จ!"
fi

# -----------------------------
# 5. ลบไฟล์ติดตั้งอัตโนมัติ (Cleanup)
# -----------------------------
echo "[*] ลบไฟล์ติดตั้ง..."
rm -f install-termux.sh
rm -rf setup
rm -f README.md
rm -rf assets

echo "[OK] ลบไฟล์ติดตั้งเรียบร้อย!"
sleep 0.5
echo "[OK] ติดตั้งระบบเสร็จสมบูรณ์"
sleep 1

# ========================================================
# ส่วนแสดงผล UI
# ========================================================

# 1. หน้าจอคำอธิบาย โปรดอ่าน
clear
echo "#################################################"
echo "#                                               #"
echo "#           คำอธิบาย โปรดอ่าน !!!                 #"
echo "#        (EXPLANATION : PLEASE READ)            #"
echo "#                                               #"
echo "#################################################"
echo ""
read -p ">>> กด Enter เพื่อดำเนินการต่อ..."

# 2. หน้าจอขอบคุณ
clear
echo "#################################################"
echo "#                                               #"
echo "#             ขอขอบคุณที่ใช้งานสคริปต์นี้               #"
echo "#                 (THANK YOU)                   #"
echo "#               by ninjamadeena                 #"
echo "#################################################"
echo ""
read -p ">>> กด Enter เพื่อดำเนินการต่อ..."

# 3. หน้าจอคู่มือและรายละเอียดไฟล์
clear
echo "================================================="
echo "           📘 คู่มือการใช้งานระบบ (MANUAL)        "
echo "================================================="
echo ""
echo "📂 รายละเอียดไฟล์ในระบบ:"
echo "   1. SMS-Fast.py  -> ยิงเร็วมากๆ"
echo "   2. SMS-Slow.py  -> ยิงช้าแต่ชัวร์"
echo "   3. SMS-Super.py -> ยิงแรงมากๆๆเร็วสุดๆ"
echo "   4. API_LIST.py  -> เก็บ API ยิงเบอร์ สำคัญสุดๆ❗❗"
echo "   5. RUN-WEB.py   -> ควบคุมผ่านหน้าเว็บ (Web Interface)"
echo "   6. index.html   -> ไฟล์หน้าเว็บหลัก"
echo "   7. favicon.jpg  -> หน้าปกเว็บไซต์"
echo "   8. update.sh    -> ใช้อัปเดตโปรแกรม"
echo "   9. API-Test.py  -> ใช้ทดสอบ API ยิงเบอร์"
echo ""
echo "📥 วิธีอัปเดต:"
echo "ใช้คำสั่ง bash ~/SMS-Spam/program/update.sh"
echo ""
echo "🔍 ระบบทดสอบ API"
echo "ใช้คำสั่ง python ~/SMS-Spam/program/API-Test.py"
echo ""
echo "-------------------------------------------------"
echo "🚀 วิธีการรันใช้งาน (เลือกได้ 2 แบบ):"
echo "-------------------------------------------------"
echo ""
echo "แบบที่ 1: ใช้งานผ่านเว็บ (ง่ายที่สุด)"
echo "   พิมพ์คำสั่ง: RUN-SMS-WEB"
echo "   (แล้วเปิด Browser ไปที่ http://localhost:8080)"
echo ""
echo "แบบที่ 2: ใช้งานผ่าน Terminal (Manual)"
echo "   1. เข้าไปที่โฟลเดอร์โปรแกรม:"
echo "      cd program"
echo ""
echo "   2. สั่งรันไฟล์ตามต้องการ:"
echo "      - ยิงแบบเร็ว: python SMS-Fast.py"
echo "      - ยิงแบบช้า: python SMS-Slow.py"
echo "      - ยิงแรงมากๆ: python SMS-Super.py"
echo ""
echo "================================================="
sleep 1
echo "[OK] พร้อมใช้งานแล้ว"
echo "================================================="
