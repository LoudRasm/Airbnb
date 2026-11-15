# TV5 — Phan Ngọc Huy

Chủ trì reviews/LLM và điều phối nhãn tay; mỗi người vẫn tự gán 20 review của mình.
Module phân tích trên main còn TODO. [Checklist chung](../FINAL_CHECKLIST.md) · Reviewer: Đức.

## Nhãn tay và text dùng để đánh giá

- [ ] Đọc [guideline](../MANUAL_LABELING.md), thông báo cách làm và gán 20 review trong [tv5.json](../../data/samples/labeling/tv5.json).
- [ ] Thu 5 PR phiếu, kiểm 20 ID/người; tổ chức người đọc thứ hai cho ca khó, ghi quyết định và chốt nhãn trước khi xem dự đoán.
- [ ] Sau các PR nhãn đã merge: chạy check/merge để tạo đúng `manual_labels.csv`, 100 dòng/hai cột; mở PR tổng hợp cho TV1 duyệt. Không điền nhãn thay bằng AI.
- [ ] Giữ text của 100 review khớp phiên bản 2026-06-15 trong phiếu. Khi dedupe reviews giữa mốc, kiểm text hash/khác phiên bản, không âm thầm dùng comments cũ cho đánh giá nhãn text mới.

## Code và kiểm chứng

- [ ] Triển khai `reviews.collect`: lọc review_id đã giao, dedupe đúng khóa, issue counts và collision; không lọc thêm theo listing_id của 1.000 listing.
- [ ] Triển khai `baseline.predict`: phương pháp không LLM, trả đúng review_id/sentiment/source; mô tả quy tắc ánh xạ về ba nhãn và giới hạn ngôn ngữ.
- [ ] Triển khai `llm.validate`/`analyze`: đúng 1.000 ID Mẫu LLM, key từ GEMINI_API_KEY, JSON có sentiment/language/positive_aspects/negative_aspects theo taxonomy config.
- [ ] Cache có model/prompt/taxonomy/text provenance; retry/timeout/JSON lỗi rõ; báo coverage/lỗi và chi phí, không biến lỗi API thành nhãn mặc định.
- [ ] Không đưa nhãn tay vào prompt; không tune prompt/từ điển trên 100 gold rồi coi kết quả là đánh giá độc lập. Nếu có dùng để chỉnh, khai báo phương pháp/giới hạn và tách dữ liệu phát triển phù hợp.
- [ ] Triển khai `evaluate.evaluate`: baseline và LLM trên cùng 100 review có nhãn; unique IDs, paired_n/manual_n, accuracy/macro-F1 và lớp không được dự đoán xử lý rõ. Thiếu dự đoán phải báo, không âm thầm thu nhỏ tập đánh giá.
- [ ] Triển khai `review_kpi.guest_kpi` có mẫu số/phạm vi. Nếu join listing không khớp, báo coverage; không suy rộng mẫu LLM thành toàn bộ review hoặc toàn Toronto.
- [ ] Triển khai `viz_reviews.render`: hình thật dùng kết quả LLM, lưu file/return list[Path], không gọi lại API trong bước vẽ.
- [ ] Thêm tests reviews/baseline/JSON/cache/retry/evaluation/missing prediction; dùng API giả trong unit test, chạy API thật riêng và ghi bằng chứng.
- [ ] Viết `reports/sections/tv5.md`: prompt/model/ngôn ngữ, quy trình nhãn, baseline, accuracy/F1, lỗi điển hình, chi phí và giới hạn; cập nhật AI_USAGE.
- [ ] Review PR calendar của Nam khi được giao; mở PR code mình, bật READY riêng từng module sau test/review.

Nhãn sentiment là phần cần gán thủ công hiện tại. Khía cạnh/ngôn ngữ do LLM trích xuất;
không giao cả nhóm gán thêm aspect/language nếu chưa có kế hoạch đánh giá riêng được thống nhất.
