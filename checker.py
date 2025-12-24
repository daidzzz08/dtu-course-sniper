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

FIREBASE_BASE_URL = "https://tool-theo-doi-slot-default-rtdb.asia-southeast1.firebasedatabase.app"
SLEEP_INTERVAL = 300 
MAX_RUNTIME = 5 * 60 * 60 + 50 * 60

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

def trigger_auto_reg(uid, class_code, reg_code):
    if not REPO_B_PAT:
        print("   ⚠️ No PAT Token, skip trigger.")
        return False
    url = f"https://api.github.com/repos/{REPO_B_OWNER}/{REPO_B_NAME}/dispatches"
    headers = { "Accept": "application/vnd.github.v3+json", "Authorization": f"token {REPO_B_PAT}" }
    payload = { "event_type": "trigger_registration", "client_payload": { "uid": uid, "class_code": class_code, "reg_code": reg_code } }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 204: print(f"   🚀 Trigger Auto-Reg Success!"); return True
        else: print(f"   ❌ Trigger Failed: {resp.status_code}"); return False
    except Exception as e: print(f"   ❌ API Error: {e}"); return False

def send_email(to_email, class_name, slots, url, reg_code):
    if not EMAIL_USER or not EMAIL_PASSWORD: return False
    msg = MIMEText(f"Hệ thống báo: {class_name} ({reg_code}) có {slots} chỗ.\nLink: {url}")
    msg['Subject'] = f"🔥 CÓ SLOT: {class_name}"
    msg['From'] = f"DTU Sniper <{EMAIL_USER}>"
    msg['To'] = to_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(EMAIL_USER, EMAIL_PASSWORD)
            s.sendmail(EMAIL_USER, to_email, msg.as_string())
        return True
    except: return False

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
                    'uid': uid, 'email': u_info.get('email'), 'req_id': r_id, 'info': r_info,
                    'is_vip': u_info.get('is_vip', False), 'has_acc': 'student_account' in u_info
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
                if not old_notified:
                    if send_email(sub['email'], name, slots, url, reg_code): new_notified = True
                if sub['is_vip'] and sub['has_acc'] and not old_triggered:
                    if trigger_auto_reg(sub['uid'], code, reg_code): new_triggered = True
            else:
                if old_notified: new_notified = False
                if old_triggered: new_triggered = False

            patch_data = {
                "last_check": get_current_time(), "name": name, "code": code, "registration_code": reg_code, "slots": slots,
                "notification_sent": new_notified, "autoreg_triggered": new_triggered
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

if __name__ == "__main__": main_loop()