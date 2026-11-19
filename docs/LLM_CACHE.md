# Tạo và kiểm cache Gemini trước khi nộp

Người phụ trách: TV5, nhóm trưởng kiểm trước khi merge. Nhóm chưa có cache thật tính đến 2026-11-16.
Không dùng fixture test, keyword baseline hoặc nhãn tay thay cho kết quả Gemini.

1. Cài môi trường theo README, chuẩn bị raw của đủ bốn mốc. Manifest phạm vi nhóm đã có trong repo;
   workbook gốc nếu có vẫn được ưu tiên. Giữ nguyên 100 nhãn tay trước khi đánh giá.
2. Cấu hình model/taxonomy trong `configs/toronto.yaml`. Model hiện tại là `gemini-3.5-flash-lite`.
   Đặt `GEMINI_API_KEY` vào môi trường trên máy người tạo cache; không commit khóa hoặc gửi vào chat.
   Chương trình không tự nạp `.env`. Lệnh tạo cache có thể sử dụng quota/chi phí API theo tài khoản.
3. Chạy từ gốc repo:

```bash
python scripts/generate_llm_cache.py --config configs/toronto.yaml
```

Script đọc reviews theo **review_id** ở từng mốc, khử trùng như pipeline và chọn đúng 1.000 ID Mẫu LLM.
Kết quả hợp lệ ghi nối ngay vào `data/processed/llm_cache.jsonl`. Nếu lỗi API/quota/JSON, sửa nguyên nhân
rồi chạy lại: các record đúng provenance được dùng lại, không gọi lại phần đã xong. Có retry hữu hạn;
không tự đổi nhãn hoặc chọn mẫu khác khi API lỗi.

4. Kiểm tra tính đầy đủ, không cần khóa và không gọi API:

```bash
python scripts/generate_llm_cache.py --config configs/toronto.yaml --check
python run_pipeline.py --config configs/toronto.yaml --no-download
```

Kiểm tra phải báo đủ 1.000 ID khớp nội dung review, model và chữ ký prompt/taxonomy. Thay prompt, model
hoặc văn bản sẽ làm cache cũ không còn khớp. Chỉ `--check` thành công chưa chứng minh các dự đoán đúng;
đọc thêm output/evaluation và phân tích lỗi thực tế.

5. Kiểm `reports/generated/real/evaluation.csv`: baseline và LLM đều đối chiếu **cùng 100 nhãn tay**.
   Lưu số đo accuracy/macro-F1, lỗi theo lớp và ví dụ, phạm vi join vùng và chi phí vào phần báo cáo TV5.
   `estimate_cost` chỉ là ước tính theo ký tự/tokens và đơn giá tham khảo, không phải hóa đơn thực tế;
   cột full_assigned_estimate nói 5.000 review được giao, không đại diện số review toàn Toronto.
6. Commit đúng cache đã kiểm, mở PR; sau merge thử clone sạch/cài/chạy một lệnh không API key:

```bash
git add data/processed/llm_cache.jsonl
git commit -m "Add validated Gemini cache for assigned review sample"
git push
```

`.gitignore` chỉ cho phép cache này, vẫn bỏ qua raw và CSV tự sinh. Không commit review thô, workbook
của toàn lớp hoặc khóa. Cache giữ ID, hash nội dung, model, prompt version/hash, taxonomy và dự đoán JSON;
không chứa toàn văn review.

Giảng viên chạy `python run_pipeline.py --config configs/toronto.yaml`: tải raw nếu thiếu, đọc cache,
xuất CSV/hình và đánh giá, không gọi Gemini. `--skip-llm` chỉ chạy phần không LLM ở thư mục riêng,
không phải lệnh thay thế cho bản nộp đầy đủ. [Checklist](FINAL_CHECKLIST.md).
