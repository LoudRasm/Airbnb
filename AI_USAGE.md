# Minh bạch sử dụng AI

## Công cụ và phạm vi

- **OpenAI Codex** hỗ trợ tạo khung repo, thiết lập luồng kiểm dữ liệu và tích hợp pipeline. Với phần TV1, Codex hỗ trợ viết mã phân tích cohort, hình biến động và kiểm thử. Codex cũng hỗ trợ triển khai phần review của TV5, biên tập báo cáo LaTeX và đối chiếu đầu ra trước khi nộp.
- **Claude** hỗ trợ TV2 viết quy tắc QA, phân tích thiếu dữ liệu, biểu đồ QA và kiểm thử tương ứng.
- **Gemini 3.5 Flash-Lite** trích xuất cảm xúc, khía cạnh khen/chê và ngôn ngữ cho 1.000 review được giao. Pipeline dùng cache đã lưu. Kết quả Gemini và baseline được đánh giá trên cùng tập 100 nhãn tay của nhóm.

## Prompt then chốt

Các yêu cầu dưới đây được tóm tắt từ quá trình làm bài.

| Công cụ | Yêu cầu chính | Tệp hoặc bước |
|---|---|---|
| Codex | Tạo khung repo cho năm thành viên và bốn mốc Toronto, có một lệnh chạy chung | `run_pipeline.py`, `configs/`, `README.md` |
| Codex | Đọc đúng danh sách ID từ workbook, tách phần kiểm tra và ghép CSV bàn giao | `scripts/check_data.py`, `src/airbnb/data_check.py` |
| Codex | Chuẩn bị phiếu gán nhãn, chia 100 ID thành năm phần và kiểm tra khi ghép | `scripts/label_reviews.py`, `docs/MANUAL_LABELING.md` |
| Codex | Tính mức hiện diện và thay đổi thuộc tính của cohort qua các mốc | `src/airbnb/analysis.py`, `src/airbnb/viz_market.py` |
| Claude | Làm sạch listings, kiểm quy tắc và vẽ tác động QA trên bốn mốc | `src/airbnb/qa.py`, `src/airbnb/eda.py`, `src/airbnb/viz_qa.py` |
| Codex | Xây luồng xử lý review, baseline, cache, đánh giá và KPI trải nghiệm | `src/airbnb/reviews.py`, `baseline.py`, `llm.py`, `evaluate.py`, `review_kpi.py` |
| Gemini | Đọc từng review và trả JSON cho cảm xúc, khía cạnh khen/chê và ngôn ngữ | Prompt trong `src/airbnb/llm.py`, đầu ra trong `data/processed/llm_cache.jsonl` |
| Codex | Rà pipeline và viết gọn báo cáo bằng bảng, ảnh và số liệu sinh từ lần chạy thật | `src/airbnb/pipeline.py`, `scripts/build_report.py`, `reports/` |

## Sai sót đã phát hiện và sửa

- Bản nháp từng đề xuất phân tích giá từ calendar và dùng 200 nhãn. Nhóm đối chiếu đề và workbook rồi giới hạn phân tích giá ở listings mốc cuối, dùng 100 nhãn tay được giao.
- Mã QA ban đầu tính trung vị “trước xử lý” sau khi đã sửa giá. Ca kiểm thử có giá ngoại lai phát hiện lỗi và bảng QA được sửa để đo đúng trước và sau.
- Nhận định “giá thiếu không ngẫu nhiên” vượt quá bằng chứng. Báo cáo giới hạn kết luận ở các đặc điểm quan sát được trong mẫu.
- Chỉ số accuracy từng che khuất sai số lớp mixed. Trên tập nhãn tay, Gemini đạt 96% accuracy nhưng chỉ nhận đúng 3/7 review mixed. Báo cáo ghi cả hai kết quả và ma trận nhầm lẫn.

## Nhóm kiểm chứng thế nào

Nhóm chốt phạm vi theo workbook, xác nhận lại mốc tháng 12 với giảng viên và giữ nguyên các phiếu gán nhãn tay. Mỗi thành viên phụ trách phần được giao. Nhóm trưởng tích hợp các phần và đối chiếu kết quả với dữ liệu đầu vào.

Bản nộp được kiểm bằng 139 tests và chạy lại pipeline trên dữ liệu thật. CSV data check khớp bản tổng hợp ban đầu. Số liệu trong PDF được đối chiếu với CSV KPI và bảng đánh giá trên 100 nhãn tay. Xem [hồ sơ kiểm chứng](docs/VERIFICATION.md) và [báo cáo chính](reports/Nhom10_InsideAirbnb_Report.pdf).
