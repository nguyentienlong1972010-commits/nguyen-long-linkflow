# Nguyễn Long — LinkFlow

Website Flask giao diện tiếng Việt, tối neon và hiệu ứng cầu vồng RGB liên tục.

## Chạy thử trên máy
1. Cài Python 3.10+.
2. Mở terminal trong thư mục dự án.
3. Chạy:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
4. Mở `http://127.0.0.1:5000`.

## Triển khai Render
1. Tải project lên một repository GitHub.
2. Vào Render và tạo **New Web Service** từ repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 2 --threads 4 --timeout 30`
5. Sau khi deploy, thêm custom domain trong Render và cấu hình DNS theo hướng dẫn Render.

`app.ngynlng.by` chỉ hoạt động khi bạn sở hữu/quản lý tên miền đó và cấu hình DNS đúng. Không có DNS hoặc deploy tự động chỉ nhờ tên miền được ghi trong giao diện.

## Phạm vi
Ứng dụng theo dõi các HTTP redirect công khai và báo cáo lỗi. Nó không tự động vượt CAPTCHA, xác minh người dùng, hay giả lập tương tác quảng cáo. Một số website dựa vào JavaScript, cookie hoặc thao tác người dùng sẽ không trả ra URL đích qua HTTP redirect đơn thuần.

## Lưu ý vận hành
- Đây là bản MVP; trước khi mở công khai nên bổ sung rate limiting, logging có kiểm soát và bảo vệ chống lạm dụng.
- Backend chặn URL không phải HTTP(S) và cố gắng từ chối địa chỉ IP không công khai để giảm nguy cơ SSRF.
