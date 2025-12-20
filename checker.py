import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
import os
import sys

# --- CONFIG ---
FIREBASE_BASE_URL = "https://tool-theo-doi-slot-default-rtdb.asia-southeast1.firebasedatabase.app"

# Lấy bí mật từ Environment
EMAIL_USER = os.environ.get('EMAIL_USER') 
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
FIREBASE_SECRET = os.environ.get('FIREBASE_SECRET') 

# Lấy thông tin Worker từ Matrix
try:
    WORKER_ID = int(os.environ.get('WORKER_ID', 0))
    TOTAL_WORKERS = int(os.environ.get('TOTAL_WORKERS', 1))
except:
    WORKER_ID = 0
    TOTAL_WORKERS = 1

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
        # print(f"      📧 Mail sent to {to_email}")
        return True
    except Exception as e:
        print(f"      ❌ Mail error: {e}")
        return False

def check_one_class(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
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
    print(f"\n[{get_current_time()}] --- WORKER {WORKER_ID}/{TOTAL_WORKERS} STARTED ---")
    
    auth_suffix = get_auth_param()
    
    # Random sleep nhẹ để tránh tất cả worker hit server cùng 1 millisecond
    time.sleep(random.uniform(0.5, 3.0))

    # 1. Tải TOÀN BỘ dữ liệu (Users & Requests)
    try:
        users_resp = requests.get(f"{FIREBASE_BASE_URL}/users.json{auth_suffix}")
        all_requests_resp = requests.get(f"{FIREBASE_BASE_URL}/requests.json{auth_suffix}")
        
        users_data = users_resp.json() or {}
        requests_data = all_requests_resp.json() or {}
    except Exception as e:
        print(f"❌ Init Error: {e}")
        return

    # 2. Gom nhóm Request (De-duplication)
    # Map: URL -> [List of {uid, req_id, user_email, ...}]
    unique_tasks_map = {}

    for uid, user_reqs in requests_data.items():
        # Check User hợp lệ
        user_info = users_data.get(uid)
        if not user_info: continue
        expired_at = user_info.get('expired_at', 0)
        if expired_at < time.time() * 1000: continue # User hết hạn

        if not isinstance(user_reqs, dict): continue

        for req_id, req_info in user_reqs.items():
            if not isinstance(req_info, dict): continue
            url = req_info.get('url')
            if not url: continue

            if url not in unique_tasks_map:
                unique_tasks_map[url] = []
            
            # Thêm người đăng ký vào nhóm URL này
            unique_tasks_map[url].append({
                'uid': uid,
                'email': user_info.get('email'),
                'req_id': req_id,
                'info': req_info
            })

    unique_urls = list(unique_tasks_map.keys())
    total_links = len(unique_urls)
    
    print(f"📊 Stats: {len(users_data)} Users | {total_links} Unique URLs")

    # 3. Phân chia công việc (Sharding Logic)
    my_tasks = []
    for i, url in enumerate(unique_urls):
        # Nếu số thứ tự chia lấy dư cho tổng worker == ID của worker này
        if i % TOTAL_WORKERS == WORKER_ID:
            my_tasks.append(url)

    print(f"🐜 Worker {WORKER_ID} đảm nhận: {len(my_tasks)} links.")

    # 4. Thực thi
    for i, url in enumerate(my_tasks):
        subscribers = unique_tasks_map[url]
        print(f"\n[{i+1}/{len(my_tasks)}] Checking Link: ...{url[-20:]}")
        
        # CHỈ CHECK 1 LẦN DUY NHẤT
        name, code, reg_code, slots = check_one_class(url)
        
        if not name:
            print("   ⚠️ Failed to fetch.")
            continue
            
        print(f"   ✅ Result: {code} | Slots: {slots} | Subs: {len(subscribers)}")

        curr_slots = int(slots) if slots.isdigit() else 0

        # CẬP NHẬT CHO TẤT CẢ USER ĐĂNG KÝ LINK NÀY
        for sub in subscribers:
            uid = sub['uid']
            req_id = sub['req_id']
            email = sub['email']
            old_notified = sub['info'].get('notification_sent', False)
            
            new_notified = old_notified

            # Logic Mail
            if curr_slots > 0:
                if not old_notified:
                    print(f"      Title: Alerting {email}...")
                    if send_email(email, name, slots, url, reg_code):
                        new_notified = True
            else:
                if old_notified: new_notified = False # Reset

            # Patch DB
            patch_data = {
                "last_check": get_current_time(),
                "name": name, "code": code, "registration_code": reg_code, "slots": slots,
                "notification_sent": new_notified
            }
            try:
                requests.patch(f"{FIREBASE_BASE_URL}/requests/{uid}/{req_id}.json{auth_suffix}", json=patch_data, timeout=5)
            except:
                pass # Bỏ qua lỗi nhỏ để chạy tiếp
        
        time.sleep(1) # Nghỉ nhẹ giữa các link

    print(f"\n--- WORKER {WORKER_ID} FINISHED ---")

if __name__ == "__main__":
    run_worker()