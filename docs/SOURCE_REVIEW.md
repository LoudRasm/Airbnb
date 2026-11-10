# Ghi chú đối chiếu nguồn

**Phần dưới ghi lịch sử starter ngày 06/10/2026, không mô tả trạng thái hoàn thành hiện tại.**
Config hiện theo workbook nhóm có mốc thứ hai 2025-12-12; trang đề hiện ghi 2025-11-11.
Các module phân tích hiện là TODO; xem README, TEAM và VERIFICATION để biết trạng thái.

# Kiểm tra nguồn ngày 06/10/2026

ZIP upload chứa một Markdown ~24 KB, kế hoạch Toronto và phân công 5 người, không có code/data.
Giữ bản đọc được trong ORIGINAL_PLAN.md. Dates, stakeholder, 7 KPI, workstreams giữ theo ZIP.
Đối chiếu đề bài chính thức: https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html
Đề xác nhận bốn mốc Toronto và yêu cầu tải script, pipeline một lệnh, cấu hình ngày,
AI_USAGE, baseline + ít nhất 100 nhãn tay, LLM thật khi chấm, PDF ≤10 trang.
Trang thư mục https://data.insideairbnb.com/canada/on/toronto/ không mở được bằng công cụ web;
không kết luận dữ liệu không tồn tại. URL tải từng file dựng theo quy tắc của đề.
Không tải 16 file thật hoặc gọi API khi tạo starter; các bước này cần nhóm chạy/kiểm chứng.

Adapter REST đối chiếu tài liệu chính thức: https://ai.google.dev/api/generate-content
Tên biến môi trường: https://ai.google.dev/gemini-api/docs/get-started

## Đối chiếu repo nhóm 10 — 06/10/2026

Remote origin local: https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10.git
Branch local: main. Code phần lớn chưa được commit trong bản local tại thời điểm kiểm tra;
chưa kiểm tra nội dung main remote, quyền private hoặc branch protection.
Bản Markdown ở Downloads khớp phân công TV1–TV5 trong repo.
HEAD cả 16 URL (4 snapshot × listings/calendar/reviews/GeoJSON) trả HTTP 200.
Đây là kiểm tra truy cập, không phải kiểm dữ liệu/schema thật. Không tải đầy đủ hoặc gọi API LLM.
