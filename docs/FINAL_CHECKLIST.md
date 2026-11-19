# Checklist trước khi nộp

Cập nhật 2026-11-16. Trạng thái kỹ thuật chi tiết: [VERIFICATION](VERIFICATION.md).
Các checklist ngày 15/11 đã được thay bằng việc còn lại; không yêu cầu các bạn làm lại code/nhãn đã xong.

- [x] 100 nhãn tay đủ ID hợp lệ; giữ nguyên nhãn và phiếu cá nhân.
- [x] QA liên mốc, schema/reference, missingness và tác động KPI nối vào pipeline.
- [x] KPI nguồn cung/phòng/host giữ mọi mốc; giá chỉ ở `price_snapshot`.
- [x] Bảng KPI theo neighbourhood riêng; supply gồm cả listing thiếu giá.
- [x] Calendar có mẫu số đầy đủ, coverage và trạng thái không có quan sát.
- [x] LLM cache-only mặc định; generation tách riêng; không ghi kết quả rỗng đè lên lần chạy đầy đủ.
- [x] Hình sinh từ module thật; CI chạy pytest để thu cả test dạng hàm và unittest.
- [x] Đối chiếu raw và CSV kiểm tra ban đầu; ghi rõ khác biệt fingerprint workbook lịch sử.
- [ ] TV5 tạo cache Gemini thật cho đúng 1.000 review; kiểm tra và commit cache.
- [ ] TV5 chạy baseline/LLM trên cùng 100 nhãn; đọc lỗi, ghi accuracy/macro-F1, chi phí và giới hạn.
- [ ] TV1 xác nhận với giảng viên mốc `2025-12-12` trong workbook so với `2025-11-11` trên trang đề; bổ sung mốc nếu cần.
- [ ] Mỗi người đối chiếu phần báo cáo với CSV/hình mới và giải thích được toàn sản phẩm.
- [ ] TV1 chọn 5–8 KPI chính, chốt thông điệp cho bên nhận phân tích; ghép PDF ≤10 trang, nguồn/ngày/commit.
- [ ] Thử clone sạch, cài môi trường, chạy một lệnh với cache đã commit và không API key.
- [ ] Chạy lại hai phần data check lịch sử có workbook fingerprint khác nếu cần merge/nộp lại data check.
- [ ] Cập nhật AI_USAGE, commit báo cáo và chỉ tạo/push tag `final` sau khi bài thực sự hoàn tất.

Hạn ghi trên trang đề: 2026-11-22 lúc 23:59. Không dùng trạng thái READY hoặc test với cache giả
để kết luận đã hoàn thành phần Gemini thật. [README](../README.md) là hướng dẫn chạy hiện tại.
