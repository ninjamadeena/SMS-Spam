TARGET="$PREFIX/bin/RUN-SMS-WEB"
SOURCE="SMS-RUN-WEB-TERMUX.sh"

echo กําลังอัปเดต...
sleep 1
cd
rm -rf ~/SMS-Spam
git clone https://github.com/ninjamadeena/SMS-Spam.git
cd SMS-Spam

if ! command -v python >/dev/null 2>&1; then
    echo "[*] ไม่พบ Python -> กำลังติดตั้ง..."
    pkg update -y
    pkg install python -y
else
    echo "[OK] พบ Python แล้ว"
fi

if ! command -v pip >/dev/null 2>&1; then
    echo "[*] ไม่พบ pip -> กำลังติดตั้ง..."
    pkg install python-pip -y
else
    echo "[OK] พบ pip แล้ว"
fi
echo กําลังอัปเดตจาก requirements.txt

pip install -r requirements.txt

echo "[*] กำลังติดตั้งคำสั่ง RUN-SMS-WEB ..."
mv "$SOURCE" "$TARGET"
chmod +x "$TARGET"
echo "[OK] ติดตั้งคำสั่ง RUN-SMS-WEB สำเร็จ!"
echo "[*] ลบไฟล์ติดตั้ง..."
rm -f install-termux.sh
rm -f requirements.txt
rm -f README.md
rm -f example.jpg
echo "[OK] ลบไฟล์ติดตั้งเรียบร้อย!"
echo อัปเดตเสร็จแล้ว
