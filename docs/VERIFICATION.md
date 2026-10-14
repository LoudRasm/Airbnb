# Kiểm chứng starter — 06/10/2026

Python 3.13.7, virtualenv mới: cài requirements.txt thành công (không runtime dependency).
Demo bốn snapshot: 12 listing sau dedupe, 90 ngày/listing, availability 2/3.
4 unittest pass, gồm pipeline trong bản sao sạch từ working directory ngoài repo.
SVG parse XML thành công; 4 notebook parse JSON thành công.

Chưa kiểm chứng: tải dữ liệu thật, bộ nhãn tay thật, API Gemini thật, Windows,
GitHub branch protection. Cài editable package tùy chọn cần mạng để tải build backend;
không cần cài package để chạy pipeline/test.

## Repo Desktop nhóm 10 — 06/10/2026

Đã chạy lại 4 unittest: pass. Demo 4 snapshot: 12 listing sau dedupe.
Đã kiểm HTTP HEAD 16 URL dữ liệu thật: tất cả 200. Chưa kiểm nội dung dữ liệu.
Bổ sung .gitignore/.python-version/.env.example/CI bị thiếu trong bản Desktop.
Git check-ignore xác nhận raw, processed output, generated reports/figures, .env và .DS_Store bị ignore.

## Luồng kiểm tra theo workbook — 14/10/2026

10 tests pass: fixture XLSX, ID dài chính xác, review_id độc lập listing_id, bốn mốc,
ngày lỗi, thiếu file, số đếm sửa/lệch, báo cáo cột thiếu, workbook/raw thay đổi và merge chặn draft.
Chạy scripts/check_data.py --part all trên 12 raw gzip local: mọi mốc đúng
1.000 listings, 365.000 dòng calendar, 5.000 reviews; entire/private 875/125;
không có review 50/30/25/25 và price thiếu mốc cuối 20.
File nộp kiểm 16 cột, 4 dòng ngoài header. Mẫu LLM/nhãn tay đọc workbook = 1.000/100.
Không gọi API LLM. Các câu trả lời được sinh là gợi ý, cần nhóm trưởng đọc và bổ sung câu 4.
Workbook/raw vẫn ignore; chỉ source, config, docs, fixtures giả và báo cáo thống kê nhỏ vào commit.
