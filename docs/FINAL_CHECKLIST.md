# Checklist trước khi nộp

Cập nhật ngày 2026-11-22. Xem [cách kiểm chứng](VERIFICATION.md) và [đề bài](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html).

- [x] Giữ bốn mốc theo phân công. Giảng viên đã xác nhận mốc `2025-12-12` với nhóm trưởng.
- [x] Kiểm tra dữ liệu gốc bằng workbook. CSV tổng hợp khớp báo cáo data check ban đầu.
- [x] Cache có đủ 1.000 dự đoán Gemini. Đánh giá Gemini và baseline dùng cùng 100 nhãn tay.
- [x] Có QA, KPI không gian/thời gian/LLM và hình sinh tự động. `AI_USAGE.md` có ở gốc repo.
- [x] Cài môi trường mới và chạy lệnh nộp trong bản sao sạch, dùng cache đã commit, không cần khoá API.
- [x] Giữ một [PDF chính 9 trang](../reports/Nhom10_InsideAirbnb_Report.pdf), có nguồn, ngày chụp và mã commit phân tích.
- [ ] Điền hai MSSV còn trống. Nếu dùng bìa Viện, ghép đúng một trang và kiểm PDF tối đa 10 trang.
- [ ] Kiểm tra quyền truy cập của giảng viên và đường dẫn repo trong bảng nộp.
- [ ] Commit PDF cuối, đưa commit lên `main`, tạo tag `final` ở đúng commit rồi đẩy tag.

```bash
git push origin main
git tag final
git push origin final
```

Hạn theo đề là **23:59 ngày 2026-11-22**. Khi vấn đáp, mỗi thành viên cần giải thích được pipeline, số liệu và lựa chọn của cả nhóm.
