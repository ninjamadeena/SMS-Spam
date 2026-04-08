#!/data/data/com.termux/files/usr/bin/bash

# กำหนด Path หลักของโปรเจกต์
PROJECT_DIR="$HOME/SMS-Spam"

# เช็คว่ามีโฟลเดอร์ไหม ถ้าไม่มีให้แจ้งเตือน
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Error: ไม่พบโฟลเดอร์ $PROJECT_DIR"
    exit 1
fi

cd "$PROJECT_DIR" || exit

# ==========================================
# 🔄 ส่วนตรวจสอบอัปเดต (AUTO UPDATE CHECK)
# ==========================================
echo "🔍 กำลังตรวจสอบการอัปเดต..."

# ดึงข้อมูลล่าสุดจาก git (แต่ยังไม่ merge)
git fetch origin > /dev/null 2>&1

# ตรวจสอบความต่างของ Commit
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" != "$REMOTE" ]; then
    echo "⚠️  พบเวอร์ชันใหม่! (New Update Found)"
    echo "🚀 ระบบกำลังทำการอัปเดตอัตโนมัติ..."
    
    # เรียกใช้ไฟล์ update.sh ใน folder program
    if [ -f "program/update.sh" ]; then
        bash program/update.sh
        
        # หลังอัปเดตเสร็จ ให้จบการทำงานสคริปต์นี้ เพื่อให้ User รันใหม่ 
        # (หรือจะให้รันต่อเลยก็ได้ แต่แนะนำให้รันใหม่เผื่อ Environment เปลี่ยน)
        echo "✅ อัปเดตเสร็จแล้ว! กรุณารันคำสั่ง RUN-SMS-WEB ใหม่อีกครั้ง"
        exit 0
    else
        echo "❌ ไม่พบไฟล์ program/update.sh ข้ามการอัปเดต..."
    fi
else
    echo "✅ ระบบเป็นเวอร์ชันล่าสุดแล้ว"
fi

# ==========================================
# ▶️ ส่วนรันโปรแกรม (RUN WEB SERVER)
# ==========================================
echo "🚀 Starting SMS-Spam Web Server..."
cd web || exit
python RUN-WEB.py
