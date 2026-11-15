# TV3 — Nguyễn Quốc Hiếu

Module `kpi.py`/`viz_spatial.py` trên main đối chiếu còn TODO. Công việc trên branch chưa merge
không được tính là đã có ở main. [Checklist chung](../FINAL_CHECKLIST.md) · Reviewer: nhóm trưởng.

- [ ] Gán 20 review trong [tv3.json](../../data/samples/labeling/tv3.json) theo [guideline](../MANUAL_LABELING.md).
- [ ] Chạy `python scripts/label_reviews.py check --member tv3`, gửi phiếu qua PR.
- [ ] Triển khai `kpi.summarize(listings, cfg)` theo CONTRACTS: dùng cleaned listings của Đức, trả đúng cột, không đọc raw/tải lại.
- [ ] Tính số listing quan sát, giá trung vị mốc cuối kèm price_n/CAD, entire-home share và host nhiều listing trong cohort; công thức/mẫu số/phạm vi phải ghi rõ.
- [ ] Không tính giá mốc trước hoặc lấp giá thiếu; phân biệt host có nhiều listing quan sát với tổng tài sản của host ngoài cohort.
- [ ] Kiểm thực tế neighbourhood từng mốc và đối chiếu GeoJSON; báo cáo Đức có tên vùng, nên không mặc định cột rỗng toàn bộ theo starter. Báo matched/unmatched/missing và phương án xử lý.
- [ ] Giữ `analysis_area` và neighbourhood là hai khái niệm riêng. Nếu thêm breakdown neighbourhood, thống nhất schema/writer/test với TV1 để thật sự có output, không chỉ đổi tên cột.
- [ ] Triển khai `viz_spatial.render`: bản đồ/so sánh vùng từ cùng bảng đã tính, legend/đơn vị/nguồn/phạm vi rõ; lưu hình vào figures được truyền, trả list[Path].
- [ ] Test missing/invalid price, 0 mẫu hợp lệ, host trống, nhóm rỗng, nhiều mốc, denominator và vùng không join được trong `tests/test_kpi.py` hoặc file tương ứng.
- [ ] Đối chiếu KPI nền với số Đức báo cáo để phát hiện lệch phạm vi/quy tắc; tự tính lại, không chép hằng số vào source.
- [ ] Viết `reports/sections/tv3.md` có công thức, file đầu ra, hình, phát hiện và giới hạn.
- [ ] Review QA của Đức khi được giao; chỉ bật READY từng module sau test và review, rồi mở PR của mình vào main.

Nhóm cần tổng bộ KPI, bao gồm calendar/LLM của Nam và Phan Huy; không phải Hiếu tự viết đủ
5–8 KPI rồi bỏ phần của các bạn. Dùng fixture đúng cleaned schema để test khi pipeline chung còn lỗi.
