# Kế hoạch QA — Đức phụ trách

Module phân tích hiện là TODO; các quy tắc dưới là đề xuất để Đức khảo sát, kiểm chứng và
triển khai. Data check đã hoàn thành vẫn giữ nguyên và đếm dữ liệu trước cleaning.
[Hướng dẫn triển khai](IMPLEMENTATION_GUIDE.md) · [Schema](CONTRACTS.md).

Mỗi quy tắc cần ghi điều kiện, lý do, hành động và tác động số liệu. Ưu tiên gắn cờ; việc loại
bỏ/dedupe hoặc chọn dòng phải có lý do và test. Không dùng quy tắc dự kiến như kết quả đã chạy.

| Nhóm kiểm tra | Đề xuất | Người triển khai |
|---|---|---|
| Thiếu | ID/host/vùng/giá/text thiếu; phân biệt thiếu cột với giá trị trống | Đức: listings; Nam: calendar; Phan Huy: reviews |
| Kiểu sai | ID chuỗi chính xác; số/ngày parse đúng, hữu hạn; available t/f | Theo owner từng bảng |
| Trùng | Khóa trong mốc và bản ghi giữa mốc; quy tắc chọn dòng và collision | Theo owner từng bảng |
| Ngoại lai | Giá mốc cuối, minimum_nights, tọa độ; khảo sát ngưỡng và ảnh hưởng | Đức phối hợp Hiếu |
| Danh mục/schema lệch | Room type ngoài danh mục và cột/kiểu thay đổi giữa mốc | Đức |
| Bao phủ/join | Calendar thiếu ngày, review không ghép được listing, vùng không xác định | Nam/Hiếu/Phan Huy phối hợp Đức |

`qa.clean_listings` trả cleaned schema và QA report; calendar/reviews trả issue counts theo
CONTRACTS. Nhóm trưởng gom thành `reports/qa_report.csv`; thống nhất tên rule để tránh trùng.
Bảng có snapshot, rule, affected_rows, action, rows_after, median_price_before/after.
Đức cần giải thích tác động lên KPI và bổ sung contract nếu các KPI khác cần trường riêng.

Giá chỉ phân tích ở mốc cuối; thiếu giá các mốc trước không phải lỗi cần xin dữ liệu khác.
Ngưỡng `qa.price_max = 10000` CAD và `min_nights_cap = 365` là tham số khung, chưa được khảo
sát; chỉ dùng sau khi giải thích lựa chọn. Calendar không kiểm/tính giá.
`neighbourhood_cleansed` thiếu không được điền bằng mã vùng chữ nhật rồi gọi là neighbourhood.
ID không qua float; raw/workbook không bị sửa; review filter độc lập listing_id.

Đức bổ sung từ điển dữ liệu, quy tắc đã chọn, số dòng/KPI trước và sau QA vào docs/phần báo cáo.
Tests cần có trường hợp lỗi thật được mô phỏng và kết quả kỳ vọng có lý do; hình QA do
`viz_qa.py` sinh. Đọc output CSV để kiểm số liệu, không chỉ nhìn terminal hoặc CI xanh.
