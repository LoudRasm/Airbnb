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
