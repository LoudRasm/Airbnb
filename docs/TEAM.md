# Nhóm 10 — phân công theo bản kế hoạch Toronto

| Người | File chính sở hữu | KPI / kết quả | Reviewer |
|---|---|---|---|
| TV1 — Dương Nhật Huy | run_pipeline.py, configs/, io.py, download.py, analysis.py | supply/churn, integration, Git issues | TV4 — Vũ Phạm Khánh Nam |
| TV2 — Mai Anh Đức | qa.py, eda.py, docs/QA.md, docs/CONTRACTS.md | QA, dictionary, before/after | TV3 — Nguyễn Quốc Hiếu |
| TV3 — Nguyễn Quốc Hiếu | kpi.py, viz.py (spatial), notebook 03 | price, entire-home, host, spatial | TV1 — Dương Nhật Huy |
| TV4 — Vũ Phạm Khánh Nam | calendar.py, notebook 04 | availability, calendar, temporal (không dùng giá calendar) | TV5 — Phan Ngọc Huy |
| TV5 — Phan Ngọc Huy | reviews.py, llm.py, baseline.py, evaluate.py, notebook 05 | guest KPI, LLM/evaluation | TV2 — Mai Anh Đức |

Repository chung: [2627-LTXLDL-Airbnb-dse2049_1-nhom10](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10).
TV1–TV5 và tên theo thứ tự nhóm trưởng đã chốt. Mỗi người làm phần mình cho cả 4 snapshot.

**Nhiệm vụ hiện tại:** báo cáo kiểm tra đầu vào. Dùng [DATA_CHECK_WORKFLOW.md](DATA_CHECK_WORKFLOW.md)
để chạy phần riêng, xuất CSV/notes và mở PR. Nhóm trưởng ghép báo cáo cuối.
Bảng dưới đây và nhãn tay 200 review là kế hoạch cả kỳ trước đây; riêng câu 2 của báo cáo kiểm tra
phải lấy 1.000/100 trực tiếp từ workbook, không lấy số nhãn/prediction trong pipeline.
Mỗi người viết `reports/sections/tvN.md`, tạo test riêng `tests/test_tvN_*.py`.
Tách thêm `viz_spatial.py`, `viz_calendar.py`, `viz_reviews.py` khi phát triển để giảm đụng viz.py.
TV1 review thay đổi orchestration; thống nhất schema bằng issue trước khi sửa contract.

Nhãn tay: 200 review thật, 40/người. TV5 chuẩn bị guideline, assignment review_id không trùng;
mỗi người commit `data/samples/labels/tvN.csv`, TV5 hợp nhất thành manual_labels.csv và xử lý bất đồng.
Starter không tạo 200 nhãn giả. Có thể tăng llm.sample_size để đủ ít nhất 100 paired labels.

Definition of Done: chạy bốn mốc, không hard-code ngày, output đúng contract, test + demo pass,
QA/KPI được kiểm chứng, PR có reviewer, tài liệu/AI_USAGE được cập nhật.
Mọi thành viên học toàn bộ pipeline để vấn đáp; owner không phải người duy nhất hiểu module.
