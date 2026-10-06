# Nhóm 10 — phân công theo bản kế hoạch Toronto

| Người | File chính sở hữu | KPI / kết quả | Reviewer |
|---|---|---|---|
| TV1 | run_pipeline.py, configs/, io.py, download.py, analysis.py | supply/churn, integration, Git issues | TV4 |
| TV2 | qa.py, eda.py, docs/QA.md, docs/CONTRACTS.md | QA, dictionary, before/after | TV3 |
| TV3 | kpi.py, viz.py (spatial), notebook 03 | price, entire-home, host, spatial | TV1 |
| TV4 | calendar.py, notebook 04 | 30/90-day, weekend, temporal | TV5 |
| TV5 | reviews.py, llm.py, baseline.py, evaluate.py, notebook 05 | guest KPI, LLM/evaluation | TV2 |

Repository chung: [2627-LTXLDL-Airbnb-dse2049_1-nhom10](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10).
TV1–TV5 theo bản phân công, chưa có tên/MSSV được cung cấp. Điền tên thật trong issue; mỗi người làm module cho cả 4 snapshot.
Mỗi người viết `reports/sections/tvN.md`, tạo test riêng `tests/test_tvN_*.py`.
Tách thêm `viz_spatial.py`, `viz_calendar.py`, `viz_reviews.py` khi phát triển để giảm đụng viz.py.
TV1 review thay đổi orchestration; thống nhất schema bằng issue trước khi sửa contract.

Nhãn tay: 200 review thật, 40/người. TV5 chuẩn bị guideline, assignment review_id không trùng;
mỗi người commit `data/samples/labels/tvN.csv`, TV5 hợp nhất thành manual_labels.csv và xử lý bất đồng.
Starter không tạo 200 nhãn giả. Có thể tăng llm.sample_size để đủ ít nhất 100 paired labels.

Definition of Done: chạy bốn mốc, không hard-code ngày, output đúng contract, test + demo pass,
QA/KPI được kiểm chứng, PR có reviewer, tài liệu/AI_USAGE được cập nhật.
Mọi thành viên học toàn bộ pipeline để vấn đáp; owner không phải người duy nhất hiểu module.
