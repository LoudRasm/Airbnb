# Phạm vi kiểm chứng — 14/10/2026

## Khung hiện tại

Python 3.13.7. Các lệnh kiểm tra ở gốc repo:

```bash
python -m unittest discover -s tests -v
python run_pipeline.py --status
python run_pipeline.py --status --skip-llm
git diff --check
```

Bộ nền hiện có 11 tests: 6 data check và 5 pipeline/loader. Data check kiểm fixture XLSX,
ID dài, lọc review_id độc lập listing_id, đếm trước cleaning, lỗi dữ liệu và chặn tổng hợp sai/cũ.
Test pipeline dùng hàm giả để kiểm import/schema/xuất file, phạm vi ID và dừng khi còn TODO.
Chúng không chứng minh thuật toán QA/KPI/calendar/LLM của thành viên đã hoàn thành.
`--status` không đọc raw/gọi API; pipeline thật và demo đều dừng khi module bắt buộc chưa READY.

Lần chỉnh tài liệu hiện tại kiểm thêm: link local, đường dẫn output/lệnh/interface, mẫu PR,
phân công và tính nhất quán giữa README/TEAM/Git workflow/backlog. Giữ source phân tích ở TODO,
không tải lại raw, không ghi đè báo cáo data check hoặc chạy API.

## Data check đã chạy trên raw local

Ngày 14/10/2026, luồng kiểm đầu vào đã đọc 12 CSV gzip theo workbook của nhóm:
1.000 listings, 365.000 dòng calendar và 5.000 reviews mỗi mốc; entire/private 875/125.
Listing không có review theo bốn mốc: 50/30/25/25; thiếu price mốc cuối: 20.
Mẫu LLM/nhãn tay lấy workbook: 1.000/100. CSV tổng hợp kiểm 16 cột, 4 dòng ngoài header.
Không gọi API LLM; câu trả lời sinh tự động cần nhóm trưởng đọc trước nộp.
Script/kết quả đã merge của Nam và Đức giữ nguyên, không coi là thuật toán phân tích cả kỳ.

## Chưa xác nhận

- Thuật toán và số liệu/hình phân tích thật; Gemini API/cache/evaluation trên 100 nhãn thật.
- KPI theo neighbourhood, ý nghĩa churn trong cohort cố định và chạy mốc ngoài workbook.
- Toàn bộ môi trường Windows, quyền private/giảng viên và branch protection GitHub.
- Clone sạch chạy toàn pipeline có LLM và tái tạo báo cáo cuối.

Owner bổ sung test thuật toán có ý nghĩa vào PR. Chỉ sau kiểm chứng tích hợp/dữ liệu thật mới
cập nhật trạng thái hoàn thành; CI nền xanh và data check đạt không thay bước này.

## Lịch sử tham khảo

Starter ngày 06/10/2026 từng có implementation AI chạy demo và kiểm HTTP HEAD các URL;
những kết quả đó thuộc phiên bản cũ. Module phân tích đã chuyển về TODO theo yêu cầu nhóm trưởng.
Lịch sử chi tiết còn trong Git và SOURCE_REVIEW/AI_USAGE; không dùng demo cũ làm bằng chứng
khả năng chạy của khung hiện tại hoặc kết quả thật của thành viên.
