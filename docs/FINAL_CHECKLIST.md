# Checklist trước khi nộp

Xem [hồ sơ kiểm chứng](VERIFICATION.md) và [đề bài](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html).

- [x] Giữ bốn mốc theo phân công. Giảng viên đã xác nhận mốc `2025-12-12` với nhóm trưởng.
- [x] Kiểm tra dữ liệu gốc bằng workbook. CSV tổng hợp khớp báo cáo data check ban đầu.
- [x] Cache có đủ 1.000 dự đoán Gemini. Đánh giá Gemini và baseline dùng cùng 100 nhãn tay.
- [x] Có QA, KPI không gian/thời gian/LLM và hình sinh tự động. `AI_USAGE.md` có ở gốc repo.
- [x] Cài môi trường mới và chạy lệnh nộp trong bản sao sạch, dùng cache đã commit, không cần khoá API.
- [x] Giữ một [PDF chính 9 trang](../reports/Nhom10_InsideAirbnb_Report.pdf), có nguồn, ngày chụp và mã commit phân tích.
- [x] Điền đủ MSSV của năm thành viên và kiểm lại trang thông tin nhóm trong PDF.
- [ ] Kiểm tra quyền truy cập của giảng viên và đường dẫn repo trong bảng nộp.

Mốc nộp được đánh dấu bằng tag `final` trên commit bàn giao của nhánh `main`. Bản PDF 9 trang dùng bố cục của nhóm và nằm trong giới hạn 10 trang.

Hạn theo đề là **23:59 ngày 2026-11-22**. Khi vấn đáp, mỗi thành viên cần giải thích được pipeline, số liệu và lựa chọn của cả nhóm.
