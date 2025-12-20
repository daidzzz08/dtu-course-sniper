import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import os

# --- CẤU HÌNH FIREBASE ---
FIREBASE_DB_URL = "https://tool-theo-doi-slot-default-rtdb.asia-southeast1.firebasedatabase.app/mon_hoc.json"
FIREBASE_PATCH_URL = "https://tool-theo-doi-slot-default-rtdb.asia-southeast1.firebasedatabase.app/mon_hoc"

# --- CẤU HÌNH EMAIL (Lấy từ biến môi trường GitHub Secrets) ---
EMAIL_USER = os.environ.get('EMAIL_USER') 
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Referer': 'https://courses.duytan.edu.vn/'
}

def get_current_time():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz).strftime("%H:%M %d/%m")

def send_email_notification(class_name, slots, url, reg_code):
    """Hàm gửi email cảnh báo"""
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("⚠️ Chưa cấu hình Email trong Secrets, bỏ qua bước gửi mail.")
        return False

    subject = f"🚨 CÓ SLOT: {class_name} (Còn {slots} chỗ)"
    body = f"""
    Hệ thống phát hiện lớp học có chỗ trống!
    
    - Môn học: {class_name}
    - Số slot: {slots}
    - Mã đăng ký: {reg_code}
    
    👉 Đăng ký ngay: {url}
    
    (Email tự động từ DTU Course Sniper)
    """

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f"DTU Sniper <{EMAIL_USER}>"
    msg['To'] = EMAIL_USER # Gửi cho chính mình

    try:
        # Sử dụng Server Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        print(f"📧 Đã gửi email cảnh báo cho môn {class_name}!")
        return True
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")
        return False

def check_one_class(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return None, None, None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Tên môn
        title_element = soup.select_one('#ctdt-title span')
        class_name = title_element.text.strip() if title_element else "Không xác định"
        
        # 2. Mã môn
        code_element = soup.select_one('.title-1')
        class_code = "UNKNOWN"
        if code_element:
            raw_text = code_element.text.strip()
            class_code = raw_text.split('–')[0].strip() if "–" in raw_text else raw_text[:7]

        # 3. Mã đăng ký
        reg_code = "..."
        reg_td = soup.find('td', string=lambda text: text and "Mã đăng ký:" in text)
        if reg_td:
            val_td = reg_td.find_next_sibling('td')
            if val_td:
                span = val_td.find('span')
                reg_code = span.text.strip() if span else val_td.text.strip()

        # 4. Số slot
        slots = "0" 
        label_td = soup.find('td', string=lambda text: text and "Còn trống:" in text)
        if label_td:
            value_td = label_td.find_next_sibling('td')
            if value_td:
                span = value_td.find('span')
                slots = span.text.strip() if span else value_td.text.strip()
        
        return class_name, class_code, reg_code, slots

    except Exception as e:
        print(f"Error parsing: {e}")
        return None, None, None, None

def run_worker():
    print(f"\n[{get_current_time()}] --- START WORKER ---")
    
    try:
        response = requests.get(FIREBASE_DB_URL)
        data = response.json()
    except Exception as e:
        print(f"❌ Lỗi kết nối Firebase: {e}")
        return

    if not data:
        print("⚠️ Database trống.")
        return

    if isinstance(data, list):
        data = {str(i): v for i, v in enumerate(data) if v is not None}

    print(f"✅ Tìm thấy {len(data)} lớp cần check.")
    
    for class_id, class_info in data.items():
        if not isinstance(class_info, dict): continue
        url = class_info.get('url')
        if not url: continue

        print(f"Checking: {class_id}...", end=" ")
        name, code, reg_code, slots = check_one_class(url)
        
        if name is None:
            print("Lỗi khi cào dữ liệu.")
            continue

        # Logic thông báo
        current_slots = int(slots) if slots.isdigit() else 0
        already_notified = class_info.get('notification_sent', False)
        
        should_send_email = False
        new_notification_status = already_notified

        if current_slots > 0:
            if not already_notified:
                # Có slot mà chưa báo -> Gửi mail
                print(f"🔥 CÓ SLOT ({current_slots}) -> Gửi mail...")
                sent = send_email_notification(name, slots, url, reg_code)
                if sent:
                    new_notification_status = True
            else:
                print(f"🔥 Có slot ({current_slots}) nhưng đã báo rồi.")
        else:
            # Hết slot -> Reset trạng thái để lần sau có slot thì báo lại
            if already_notified:
                print("🔒 Đã hết slot -> Reset trạng thái thông báo.")
                new_notification_status = False
            else:
                print(f"🔒 Hết chỗ ({slots}).")

        # Update Firebase
        update_data = {
            "last_check": get_current_time(),
            "name": name,
            "code": code,
            "registration_code": reg_code,
            "slots": slots,
            "notification_sent": new_notification_status
        }
        
        try:
            requests.patch(f"{FIREBASE_PATCH_URL}/{class_id}.json", json=update_data)
        except Exception as e:
            print(f"Lỗi lưu DB: {e}")
            
        time.sleep(1) 

    print("--- FINISH WORKER ---\n")

if __name__ == "__main__":
    run_worker()