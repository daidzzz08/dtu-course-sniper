<div align="center">
🎯 DTU Course Sniper Pro
Hệ Thống Săn Slot Tín Chỉ Đa Luồng (SaaS Platform)
<p align="center">
<b>Tự động giám sát • Báo cáo tức thì • Hoạt động 24/7 • Đa người dùng</b>
</p>
✨ Tính Năng • ⚙️ Công Nghệ • 🚀 Nguyên Lý • ⚠️ Lưu Ý • 📞 Liên Hệ
</div>
📖 Giới Thiệu
DTU Course Sniper Pro là giải pháp SaaS (Software as a Service) giúp sinh viên Đại học Duy Tân giải quyết vấn đề "đăng ký trượt" các lớp học phần quan trọng. Hệ thống sử dụng kiến trúc Worker Swarm (Bầy ong thợ) trên nền tảng Cloud để liên tục kiểm tra trạng thái lớp học và gửi cảnh báo ngay lập tức khi phát hiện slot trống.
Sứ mệnh: Giúp sinh viên không còn phải canh trực website trường thủ công thâu đêm suốt sáng.
✨ Tính Năng Nổi Bật
Tính năng
Mô tả chi tiết
🤖 Worker Swarm
Sử dụng Matrix Strategy kích hoạt nhiều Worker chạy song song, quét hàng trăm lớp học chỉ trong vài giây.
⚡ Real-time Alert
Gửi Email cảnh báo ngay lập tức tới người dùng khi phát hiện lớp có chỗ trống (hủy lớp).
🛡️ SaaS Architecture
Hệ thống phân quyền Admin/User chặt chẽ. Mỗi khách hàng có không gian dữ liệu riêng biệt.
📅 Quản Lý Hạn Dùng
Tự động khóa tài khoản khi hết hạn. Hệ thống Admin Panel cho phép gia hạn nhanh chóng (+1D, +7D, +30D).
🔒 Bảo Mật Cao
Dữ liệu được bảo vệ bằng Firebase Security Rules. Mã nguồn Backend chạy trong môi trường Isolated.
📢 Global Notify
Hệ thống Popup thông báo thời gian thực từ Admin đến toàn bộ khách hàng đang online.

🛠 Công Nghệ Sử Dụng
Dự án được xây dựng với tiêu chí Hiệu năng cao - Chi phí 0đ (Serverless):
Frontend:
HTML5 & Vanilla JS (ES6+)
Tailwind CSS (Giao diện Responsive)
Icons
Backend & Cloud:
Core Logic (Requests, BeautifulSoup4)
Cloud Cronjob & Workers
Database & Authentication
🚀 Nguyên Lý Hoạt Động
graph TD
    A[Cron Job (5 Phút/Lần)] -->|Kích hoạt| B{GitHub Actions Matrix}
    B -->|Spawn| W1[Worker 1]
    B -->|Spawn| W2[Worker 2]
    B -->|Spawn| W3[Worker 3]
    
    W1 -->|Đọc & Lọc| DB[(Firebase DB)]
    W2 -->|Đọc & Lọc| DB
    W3 -->|Đọc & Lọc| DB
    
    W1 -->|Check| DTU[Server Trường]
    W2 -->|Check| DTU
    W3 -->|Check| DTU
    
    DTU -->|Trả kết quả| W1
    
    W1 -->|Phát hiện Slot| Email[📧 Gửi Email Báo Khách]
    W1 -->|Cập nhật| DB


Lên lịch: GitHub Actions kích hoạt định kỳ (Cronjob).
Phân tán: Hệ thống chia nhỏ danh sách lớp học cho nhiều Worker xử lý song song.
Xử lý: Worker kiểm tra trạng thái lớp học trên website trường.
Báo cáo: Nếu có slot trống -> Gửi Email cho khách -> Cập nhật Database.
⚠️ Lưu Ý Quan Trọng
Để đảm bảo quyền lợi và tránh hiểu lầm, xin vui lòng đọc kỹ:
🔴 TOOL CHỈ BÁO SLOT, KHÔNG ĐĂNG KÝ HỘ. Bạn cần tự đăng nhập vào trang MyDTU để thực hiện đăng ký tín chỉ.
🟠 MIỄN TRỪ TRÁCH NHIỆM. Chúng tôi cam kết hệ thống hoạt động ổn định nhất có thể. Tuy nhiên, nếu website nhà trường bảo trì, sập, hoặc thay đổi cấu trúc, tool sẽ tạm dừng hoạt động.
🟢 CẠNH TRANH CÔNG BẰNG. Việc nhận được thông báo không đảm bảo 100% bạn sẽ đăng ký được, vì có thể có sinh viên khác nhanh tay hơn.
⚖️ License & Copyright
© 2025 DTU Sniper Pro. All Rights Reserved.
Dự án này được phát hành dưới giấy phép mạnh GNU AGPLv3.
✅ Được phép: Xem mã nguồn, học tập, chạy thử nghiệm cá nhân.
🚫 Cấm: Sao chép, sửa đổi, thương mại hóa (Closed Source) mà không công khai mã nguồn của bạn dưới cùng giấy phép AGPLv3.

</div>
<p align="center">Made with ❤️ by DaiDzzz</p>
