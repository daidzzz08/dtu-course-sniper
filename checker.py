import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import os

# --- CONFIG ---
FIREBASE_BASE_URL = "https://tool-theo-doi-slot-default-rtdb.asia-southeast1.firebasedatabase.app"

# Lấy các bí mật từ biến môi trường
EMAIL_USER = os.environ.get('EMAIL_USER') 
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
FIREBASE_SECRET = os.environ.get('FIREBASE_SECRET') 

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Referer': 'https://courses.duytan.edu.vn/'
}

def get_current_time():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz).strftime("%H:%M %d/%m")

def get_auth_param():
    return f"?auth={FIREBASE_SECRET}" if FIREBASE_SECRET else ""

def send_email(to_email, class_name, slots, url, reg_code):
    if not EMAIL_USER or not EMAIL_PASSWORD: return False
    
    subject = f"🔥 CÓ SLOT: {class_name} ({slots} chỗ)"
    body = f"""
    Hệ thống DTU Sniper Pro thông báo:
    
    Lớp học: {class_name}
    Mã ĐK: {reg_code}
    Số chỗ trống: {slots}
    
    Link đăng ký: {url}
    
    (Email tự động, vui lòng không trả lời)
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = f"DTU Sniper <{EMAIL_USER}>"
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, to_email, msg.as_string())
        print(f"   📧 Sent mail to: {to_email}")
        return True
    except Exception as e:
        print(f"   ❌ Mail error: {e}")
        return False

def check_one_class(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200: return None, None, None, None
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title_el = soup.select_one('#ctdt-title span')
        name = title_el.text.strip() if title_el else "Unknown"
        
        code_el = soup.select_one('.title-1')
        code = "..."
        if code_el:
            raw = code_el.text.strip()
            code = raw.split('–')[0].strip() if "–" in raw else raw[:7]

        reg_code = "..."
        reg_td = soup.find('td', string=lambda t: t and "Mã đăng ký:" in t)
        if reg_td:
            val = reg_td.find_next_sibling('td')
            if val: reg_code = val.text.strip()

        slots = "0"
        lbl_td = soup.find('td', string=lambda t: t and "Còn trống:" in t)
        if lbl_td:
            val = lbl_td.find_next_sibling('td')
            if val: slots = val.find('span').text.strip() if val.find('span') else val.text.strip()
            
        return name, code, reg_code, slots
    except: return None, None, None, None

def run_worker():
    print(f"\n[{get_current_time()}] --- START SAAS WORKER (SECURE MODE) ---")
    
    auth_suffix = get_auth_param()
    if not FIREBASE_SECRET:
        print("⚠️ CẢNH BÁO: Không tìm thấy FIREBASE_SECRET. Worker có thể không ghi được vào DB khóa.")

    # 1. Lấy danh sách Users
    try:
        users_resp = requests.get(f"{FIREBASE_BASE_URL}/users.json{auth_suffix}")
        if users_resp.status_code != 200:
            print(f"❌ Lỗi đọc Users: {users_resp.status_code} - {users_resp.text}")
            return
        users_data = users_resp.json()
    except Exception as e:
        print(f"❌ Connect Error: {e}")
        return

    if not users_data:
        print("⚠️ No users found.")
        return

    print(f"👥 Users loaded: {len(users_data)}")

    for uid, user_info in users_data.items():
        if not isinstance(user_info, dict): continue
        
        email = user_info.get('email', 'unknown')
        expired_at = user_info.get('expired_at', 0)
        
        # Check hạn sử dụng
        if expired_at < time.time() * 1000:
            # print(f"⛔ Skip expired: {email}")
            continue
            
        print(f"\n👤 {email}...", end="")
        
        # 3. Lấy requests của user
        try:
            req_resp = requests.get(f"{FIREBASE_BASE_URL}/requests/{uid}.json{auth_suffix}")
            requests_data = req_resp.json()
        except: continue
        
        if not requests_data:
            print(" (Empty)", end="")
            continue
            
        count = 0
        for req_id, req_info in requests_data.items():
            if not isinstance(req_info, dict): continue
            url = req_info.get('url')
            if not url: continue
            
            name, code, reg_code, slots = check_one_class(url)
            count += 1
            
            if not name: continue

            # Logic Mail
            curr_slots = int(slots) if slots.isdigit() else 0
            notified = req_info.get('notification_sent', False)
            new_notified = notified
            
            if curr_slots > 0:
                print(f" [🔥 SLOT! {code}]", end="")
                if not notified:
                    if send_email(email, name, slots, url, reg_code):
                        new_notified = True
            else:
                if notified: new_notified = False 

            # Update DB (Dùng auth secret)
            patch_data = {
                "last_check": get_current_time(),
                "name": name, "code": code, "registration_code": reg_code, "slots": slots,
                "notification_sent": new_notified
            }
            
            try:
                # Thêm timeout và check status code
                patch_res = requests.patch(f"{FIREBASE_BASE_URL}/requests/{uid}/{req_id}.json{auth_suffix}", json=patch_data, timeout=10)
                if patch_res.status_code != 200:
                    print(f" ❌ Failed to update DB: {patch_res.status_code}", end="")
            except Exception as e:
                print(f" ❌ Update Error: {e}", end="")

            time.sleep(0.5) 
        
        print(f" Done ({count} classes).")

    print("\n--- FINISH ---")

if __name__ == "__main__":
    run_worker()