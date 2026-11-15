# TV1 — Dương Nhật Huy, nhóm trưởng

Việc của bạn gồm phần cá nhân và finalize sau khi các bạn đã tự hoàn thiện/PR.
[Checklist chung](../FINAL_CHECKLIST.md) · [Hướng dẫn nhãn](../MANUAL_LABELING.md).

## Phần cá nhân

- [ ] Gán 20 review trong [tv1.json](../../data/samples/labeling/tv1.json), chạy `python scripts/label_reviews.py check --member tv1`.
- [ ] Chốt bên nhận phân tích, câu hỏi và ý nghĩa từng KPI với cả nhóm; tổng bộ KPI gồm phần Hiếu/Nam/Phan Huy, không giao 5–8 KPI riêng cho từng người.
- [ ] Thiết kế `analysis.churn` hoặc thay bằng chỉ số biến động quan sát phù hợp. Cohort 1.000 ID cố định không đủ đo entry/exit toàn Toronto; đổi metric thì sửa contract/writer/tests đồng bộ.
- [ ] Hoàn thiện `viz_market.render`; lưu hình đúng figures được truyền vào, trả list[Path], kiểm số liệu trên hình.
- [ ] Test phần analysis và viết `reports/sections/tv1.md`: công thức, phạm vi, lệnh chạy, phát hiện/giới hạn.

## Điều phối PR, không làm thay lỗi cá nhân

- [ ] Giao Nam sửa calendar; theo dõi bằng PR của Nam, không gỡ lỗi cú pháp/giá thay trong đợt này.
- [ ] Đức chốt output QA; Hiếu/Phan Huy/Nam giữ contract. Đổi schema phải có owner downstream review.
- [ ] Review trạng thái từng module độc lập; READY chỉ là cờ kỹ thuật, không thay kiểm logic/dữ liệu.
- [ ] Duyệt PR nhãn từng người và PR TV5 ghép CSV; không nhận ảnh thay file nhãn/code.

## Finalize sau khi PR thành viên đã merge

- [ ] Nối các bước QA đã có: schema drift, cross-snapshot, missingness, KPI impact và tham chiếu GeoJSON từng mốc. Hiện pipeline mới gọi clean_listings/profile, không tự gọi đủ các helper của Đức.
- [ ] Phối hợp Đức tránh chạy cleaning hai lần; chọn một điểm điều phối trả bảng và ghi đủ CSV đầu ra.
- [ ] Kiểm 30/90 ngày: config hiện chỉ truyền window_days=90; nếu bổ sung 30 ngày, nối thật và cập nhật schema/output, không chỉ ghi trong báo cáo.
- [ ] Kiểm reviews independent listing IDs, dedupe/text version; guest KPI không âm thầm bỏ review không join được.
- [ ] Kiểm mẫu 1.000 LLM, 100 nhãn thật, baseline/LLM cùng ID, nhãn khóa trước đánh giá và cache/API chạy thật.
- [ ] Kiểm lại toàn tests/status sau Nam sửa; không lấy kết quả 42 test QA thay toàn bộ integration.
- [ ] Chạy pipeline thật từ main; kiểm metadata/CSV/hình và tái lập trong clone sạch.
- [ ] Xác minh bài kiểm mốc khác: loader hiện buộc ngày trùng workbook; trao đổi quy tắc assignment và sửa thiết kế có test, không bỏ guard tùy tiện.
- [ ] Hợp nhất phần báo cáo các bạn thành `reports/report.pdf`, rà nguồn/ngày/commit, giới hạn, AI_USAGE và checklist cuối trong FINAL_CHECKLIST.
- [ ] Tạo tag final chỉ sau khi mọi kết quả đã được duyệt và báo cáo khớp mã source.

Đầu ra bàn giao: code tích hợp, test analysis/integration, tv1.md, bảng/hình tổng hợp và bản nộp cuối.
