import requests
import json
import time

# --- CẤU HÌNH ---
FIREBASE_BASE_URL = "https://tool-theo-doi-slot-default-rtdb.asia-southeast1.firebasedatabase.app"

def promote_to_admin():
    print("--- TOOL THĂNG CẤP ADMIN ---")
    email_input = input("Nhập email tài khoản bạn muốn set làm Admin: ").strip()
    
    if not email_input:
        print("Vui lòng nhập email!")
        return

    # 1. Tìm UID của email này trong Database users
    print(f"Đang tìm user: {email_input}...")
    try:
        users_resp = requests.get(f"{FIREBASE_BASE_URL}/users.json")
        users_data = users_resp.json()
    except Exception as e:
        print(f"Lỗi kết nối: {e}")
        return

    if not users_data:
        print("Database trống! Bạn hãy lên web ĐĂNG KÝ tài khoản trước.")
        return

    target_uid = None
    current_data = None

    for uid, info in users_data.items():
        if info.get('email') == email_input:
            target_uid = uid
            current_data = info
            break
    
    if not target_uid:
        print("❌ Không tìm thấy email này trong hệ thống!")
        print("Gợi ý: Hãy chắc chắn bạn đã đăng ký trên web index.html thành công.")
        return

    print(f"✅ Đã tìm thấy UID: {target_uid}")

    # 2. Update Role và Hạn sử dụng
    update_data = {
        "role": "admin",
        "expired_at": 9999999999999  # Năm 2286 (Vĩnh viễn)
    }

    try:
        requests.patch(f"{FIREBASE_BASE_URL}/users/{target_uid}.json", json=update_data)
        print("\n🎉 THÀNH CÔNG!")
        print(f"Tài khoản {email_input} đã trở thành ADMIN.")
        print("Hạn sử dụng: Vĩnh viễn.")
    except Exception as e:
        print(f"Lỗi update: {e}")

if __name__ == "__main__":
    promote_to_admin()