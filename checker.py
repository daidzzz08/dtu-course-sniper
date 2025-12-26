import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys

# --- CONFIG ---
FIREBASE_BASE_URL = "https://tool-theo-doi-slot-default-rtdb.asia-southeast1.firebasedatabase.app"
SLEEP_INTERVAL = 300 
MAX_RUNTIME = 5 * 60 * 60 + 50 * 60

# --- SECRETS ---
EMAIL_USER = os.environ.get('EMAIL_USER') 
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
FIREBASE_SECRET = os.environ.get('FIREBASE_SECRET') 
REPO_B_PAT = os.environ.get('REPO_B_PAT')
REPO_B_OWNER = os.environ.get('REPO_B_OWNER', 'daidzzz08')
REPO_B_NAME = os.environ.get('REPO_B_NAME', 'auto-register-class')

try:
    WORKER_ID = int(os.environ.get('WORKER_ID', 0))
    TOTAL_WORKERS = int(os.environ.get('TOTAL_WORKERS', 1))
except:
    WORKER_ID = 0; TOTAL_WORKERS = 1

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'Referer': 'https://courses.duytan.edu.vn/'
}

def get_current_time():
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(tz).strftime("%H:%M %d/%m")

def get_auth_param():
    return f"?auth={FIREBASE_SECRET}" if FIREBASE_SECRET else ""

# --- HÀM GỬI EMAIL HTML (MỚI) ---
def send_email_html(to_email, class_name, slots, url, reg_code):
    if not EMAIL_USER or not EMAIL_PASSWORD: return False
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🔥 CÓ SLOT: {class_name} ({slots} chỗ)"
    msg['From'] = f"DTU Sniper Pro <{EMAIL_USER}>"
    msg['To'] = to_email

    # Nội dung Text thuần (Fallback)
    text_content = f"""
    Hệ thống phát hiện slot trống!
    Môn: {class_name}
    Mã ĐK: {reg_code}
    Số chỗ: {slots}
    Link: {url}
    """

    # Nội dung HTML (Đẹp)
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
          
          <!-- Header -->
          <div style="background-color: #2563EB; padding: 20px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 24px;">DTU SNIPER PRO 🎯</h2>
          </div>

          <!-- Body -->
          <div style="padding: 30px;">
            <h3 style="color: #d32f2f; text-align: center; margin-top: 0;">🔥 PHÁT HIỆN SLOT TRỐNG!</h3>
            
            <div style="background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; margin: 20px 0;">
              <p style="margin: 10px 0; font-size: 16px;"><strong>Môn học:</strong> {class_name}</p>
              <p style="margin: 10px 0; font-size: 16px;">
                <strong>Mã đăng ký:</strong> 
                <span style="background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 4px; font-family: monospace; font-size: 18px; font-weight: bold;">{reg_code}</span>
              </p>
              <p style="margin: 10px 0; font-size: 16px;">
                <strong>Số chỗ còn lại:</strong> 
                <span style="color: #16a34a; font-size: 20px; font-weight: bold;">{slots}</span>
              </p>
            </div>

            <p style="text-align: center; color: #64748b; font-size: 14px; margin-bottom: 30px;">
              Hệ thống phát hiện vào lúc: {get_current_time()}
            </p>

            <!-- Button -->
            <div style="text-align: center;">
              <a href="{url}" style="background-color: #2563EB; color: white; padding: 14px 28px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; display: inline-block;">
                Đăng nhập MyDTU Ngay
              </a>
            </div>
          </div>

          <!-- Footer -->
          <div style="background-color: #f1f5f9; padding: 15px; text-align: center; font-size: 12px; color: #94a3b8;">
            <p>Đây là email tự động. Vui lòng không trả lời email này.</p>
            <p>© 2025 DTU Sniper Pro - Admin: Nguyễn Phát Đại</p>
          </div>
        </div>
      </body>
    </html>
    """

    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')

    msg.attach(part1)
    msg.attach(part2)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(EMAIL_USER, EMAIL_PASSWORD)
            s.sendmail(EMAIL_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"      ❌ Mail Error: {e}")
        return False

# --- HÀM TRIGGER (UPDATE: Gửi kèm Email) ---
def trigger_auto_reg(uid, class_code, reg_code, user_email):
    if not REPO_B_PAT:
        print("   ⚠️ No PAT Token, skip trigger.")
        return False
    
    url = f"https://api.github.com/repos/{REPO_B_OWNER}/{REPO_B_NAME}/dispatches"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {REPO_B_PAT}"
    }
    
    # Payload bây giờ có thêm 'email' để Repo B biết đường báo tin
    payload = {
        "event_type": "trigger_registration",
        "client_payload": {
            "uid": uid,
            "class_code": class_code,
            "reg_code": reg_code,
            "email": user_email 
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 204:
            print(f"   🚀 Trigger Auto-Reg Success (Email: {user_email})")
            return True
        else:
            print(f"   ❌ Trigger Failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"   ❌ API Error: {e}")
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

def run_batch():
    print(f"\n[{get_current_time()}] --- BATCH STARTED (Worker {WORKER_ID}) ---")
    auth_suffix = get_auth_param()
    
    try:
        users_resp = requests.get(f"{FIREBASE_BASE_URL}/users.json{auth_suffix}")
        reqs_resp = requests.get(f"{FIREBASE_BASE_URL}/requests.json{auth_suffix}")
        users_data = users_resp.json() or {}
        reqs_data = reqs_resp.json() or {}
    except: print("❌ DB Error"); return

    unique_map = {}
    for uid, u_reqs in reqs_data.items():
        u_info = users_data.get(uid)
        if not u_info: continue
        if u_info.get('expired_at', 0) < time.time()*1000: continue

        if not isinstance(u_reqs, dict): continue
        for r_id, r_info in u_reqs.items():
            if not isinstance(r_info, dict): continue
            url = r_info.get('url')
            if url:
                if url not in unique_map: unique_map[url] = []
                unique_map[url].append({
                    'uid': uid, 
                    'email': u_info.get('email'), 
                    'req_id': r_id, 
                    'info': r_info,
                    'is_vip': u_info.get('is_vip', False), 
                    'has_acc': 'student_account' in u_info
                })

    unique_urls = list(unique_map.keys())
    my_tasks = [u for i, u in enumerate(unique_urls) if i % TOTAL_WORKERS == WORKER_ID]
    print(f"🐜 Task: {len(my_tasks)} links.")

    for url in my_tasks:
        name, code, reg_code, slots = check_one_class(url)
        if not name: continue
        
        curr_slots = int(slots) if slots.isdigit() else 0
        
        for sub in unique_map[url]:
            old_notified = sub['info'].get('notification_sent', False)
            old_triggered = sub['info'].get('autoreg_triggered', False)
            new_notified = old_notified
            new_triggered = old_triggered

            if curr_slots > 0:
                # 1. Gửi Email HTML (Nếu chưa báo)
                if not old_notified:
                    print(f"      📧 Emailing {sub['email']}...")
                    if send_email_html(sub['email'], name, slots, url, reg_code): 
                        new_notified = True
                
                # 2. Trigger Auto-Reg (Kèm email)
                if sub['is_vip'] and sub['has_acc'] and not old_triggered:
                    print(f"      👑 VIP DETECTED: {sub['email']} -> Triggering Auto-Reg...")
                    # Truyền thêm email vào hàm trigger
                    if trigger_auto_reg(sub['uid'], code, reg_code, sub['email']): 
                        new_triggered = True
            else:
                if old_notified: new_notified = False
                if old_triggered: new_triggered = False

            patch_data = {
                "last_check": get_current_time(),
                "name": name, "code": code, "registration_code": reg_code, "slots": slots,
                "notification_sent": new_notified,
                "autoreg_triggered": new_triggered
            }
            try: requests.patch(f"{FIREBASE_BASE_URL}/requests/{sub['uid']}/{sub['req_id']}.json{auth_suffix}", json=patch_data, timeout=5)
            except: pass
        
        time.sleep(1)

def main_loop():
    print(f"🚀 WORKER {WORKER_ID}/{TOTAL_WORKERS} RUNNING...")
    start_time = time.time()
    while True:
        if time.time() - start_time > MAX_RUNTIME: break
        run_batch()
        print(f"💤 Sleep {SLEEP_INTERVAL}s..."); time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main_loop()