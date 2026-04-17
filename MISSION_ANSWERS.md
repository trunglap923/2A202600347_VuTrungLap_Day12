# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Các lỗi thiết kế (Anti-patterns) tìm thấy

1. **Lộ bí mật (Hardcoded Secrets)**: API key và Database URL được viết trực tiếp trong code (dòng 17-18). Điều này rất nguy hiểm nếu code được đẩy lên GitHub.
2. **Thiếu quản lý cấu hình (No Config Management)**: Các tham số như `DEBUG`, `MAX_TOKENS` được fix cứng thay vì dùng biến môi trường, gây khó khăn khi thay đổi cấu hình mà không sửa code.
3. **Logging không chuyên nghiệp**: Dùng `print()` thay vì thư viện logging. Đặc biệt nguy hiểm khi in (print) cả API key ra console (dòng 34).
4. **Thiếu Health Check Endpoint**: Không có endpoint `/health` hoặc `/ready`, khiến các nền tảng Cloud không thể giám sát trạng thái để tự động khởi động lại khi app lỗi.
5. **Cố định Port và Host**: Fix cứng port `8000` và host `localhost`, khiến ứng dụng không thể nhận kết nối từ bên ngoài khi chạy trong Docker hoặc trên Cloud (cần `0.0.0.0`).
6. **Xử lý tham số sai cách**: Dùng Query parameter cho dữ liệu trong yêu cầu POST, dẫn đến lỗi 422 khi gửi dữ liệu qua JSON Body và không bảo mật cho dữ liệu nhạy cảm.

### Exercise 1.3: Bảng so sánh giữa Develop và Production

| Tính năng             | Bản Develop             | Bản Production                     | Tại sao quan trọng?                                                            |
| --------------------- | ----------------------- | ---------------------------------- | ------------------------------------------------------------------------------ |
| **Cấu hình (Config)** | Hardcode trong code     | Biến môi trường (`.env`)           | Bảo mật key nhạy cảm và linh hoạt giữa các môi trường dev/prod.                |
| **Health check**      | Không có                | Có `/health` và `/ready`           | Giúp hệ thống monitor (nền tảng cloud/k8s) biết khi nào cần restart container. |
| **Logging**           | `print()` (Text thuần)  | JSON Structured Logging            | Dễ dàng lọc và phân tích log bằng các công cụ tập trung.                       |
| **Shutdown**          | Ngắt đột ngột           | Graceful shutdown (xử lý tín hiệu) | Giúp hoàn thành các request đang xử lý dở dang trước khi tắt máy.              |
| **Binding IP**        | `localhost` (127.0.0.1) | `0.0.0.0`                          | Cần thiết để Docker và Cloud có thể route traffic vào ứng dụng.                |

---

## Part 2: Docker

_(Đang thực hiện...)_
