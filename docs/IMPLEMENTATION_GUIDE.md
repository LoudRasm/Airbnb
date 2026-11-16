# Phát triển trên source chung

Các module đã có implementation. Mỗi thành viên tiếp tục sửa module theo [TEAM](TEAM.md)
trên branch riêng, thêm test có ca lỗi thực tế, mở PR vào main. Không chép thuật toán vào runner
hoặc tạo một bản source riêng theo tên người. Lịch sử Git giữ nguyên đóng góp trước đây.

`run_pipeline.py` nhận tham số; `airbnb.pipeline.run` điều phối; `outputs.csv_outputs` định nghĩa
schema CSV; `labels.manual_labels` đọc và kiểm tra nhãn. Thuật toán nằm trong module của owner,
đầu vào/đầu ra theo [CONTRACTS](CONTRACTS.md). Import trong package dùng relative import.

Luồng chung gọi `qa.run_listings_qa` một lần cho tất cả mốc (bao gồm schema/cross/reference),
calendar xử lý streaming từng mốc, reviews dedupe theo ID độc lập, rồi KPI/baseline/cache/evaluation.
Hàm nghiệp vụ trả bảng và diagnostics; runner ghi file. `viz.render_all` gọi các module vẽ;
không tải dữ liệu, gọi API hoặc tính lại một bản công thức KPI khác trong bước vẽ.

Khi thêm/đổi cột, cập nhật `outputs.py`, CONTRACTS và test trong cùng PR. Giữ ID là chuỗi,
config là nguồn của ngày/đường dẫn/giới hạn. Calendar không lấy giá. LLM bình thường chỉ đọc cache;
API chỉ dùng trong lệnh tạo cache riêng, tuyệt đối không dùng nhãn tay làm dự đoán.

```bash
python -m pytest -q
python run_pipeline.py --status
python run_pipeline.py --demo --skip-llm
python run_pipeline.py --skip-llm --no-download
```

Demo và fixture nhỏ là dữ liệu giả, chỉ chứng minh hành vi phần mềm. Kết quả thật cần đối chiếu
CSV, metadata, mẫu số và báo cáo. READY là tín hiệu tích hợp, không xác nhận peer review học thuật,
chất lượng kết luận hoặc sự đầy đủ của cache. [Việc còn lại](FINAL_CHECKLIST.md).

CSV/hình đầu ra thuộc từng chế độ riêng như README. Không chép terminal vào notebook để bàn giao;
notebook đọc kết quả đã sinh hoặc chạy hàm nghiệp vụ để khám phá bổ trợ.
