# Từ starter đến bài nộp

Starter chạy demo offline và có adapter LLM, nhưng chưa kiểm chứng dữ liệu/API thật.

1. TV1: tải thật đủ 16 file, kiểm manifest và schema, đo thời gian/RAM; thử snapshot mới.
2. TV2: khảo sát data dictionary, hoàn thiện 15–20 QA rule và KPI impact, referential integrity.
3. TV3: median theo room type, choropleth có join neighbourhood và kiểm unmatched;
   dùng projection phù hợp, legend/caption, spatial insight thật.
4. TV4: tối ưu calendar lớn (SQLite/Polars khi cần), 30/90d, weekend pricing, coverage.
5. TV5: điều chỉnh model/taxonomy/prompt, tăng sample đủ paired labels, retry timeout/invalid JSON,
   cache provenance/token usage và ước tính chi phí bằng giá nhà cung cấp tại thời điểm chạy.
6. Cả nhóm: 200 nhãn tay thật (40/người), guideline + adjudication, đánh giá cùng mẫu cho
   baseline và LLM, accuracy/macro-F1 + aspect/language quality + error analysis.
7. Viết từng reports/sections/tvN.md, ghép PDF ≤10 trang, ghi nguồn + snapshot + commit.
8. Chạy clean clone thật có LLM bằng key khác, đối chiếu report, AI_USAGE, final tag.

Không có 100 nhãn thật hoặc API chưa chạy nghĩa là phần LLM chưa hoàn thành yêu cầu chấm.
Notebook placeholder là JSON notebook hợp lệ; muốn chạy tương tác có thể cài Jupyter riêng,
nhưng không thêm dependency vào pipeline nếu chỉ phục vụ khám phá.
