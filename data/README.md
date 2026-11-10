# Quy ước dữ liệu nhóm 10

## Raw và workbook trên mỗi máy

```text
data/
  assignments/assignment.xlsx        Workbook gốc giảng viên, giữ nguyên
  raw/
    2025-09-11/
    2025-12-12/
    2026-03-19/
    2026-06-15/
```

Mỗi folder ngày chứa `listings.csv.gz`, `calendar.csv.gz`, `reviews.csv.gz` và
`neighbourhoods.geojson`. Downloader tạo đúng đường dẫn từ `configs/toronto.yaml`.
Đã tải CSV thì đặt vào đúng folder và giữ tên chuẩn; chỉ bổ sung file còn thiếu khi cần.
Data check cần ba CSV; pipeline phân tích còn kiểm GeoJSON. Không đổi đuôi gzip hoặc tên thành
`calendarYYYY-MM-DD.csv.gz`. Config/workbook dùng ngày YYYY-MM-DD và mã DSE2049-C01-G10-toronto.

Raw/workbook được gitignore. Clone/pull không mang chúng theo; mỗi máy chuẩn bị bản gốc cùng
phiên bản. Không mở rồi lưu lại workbook/CSV bằng Excel; ID dài đọc như chuỗi, không qua float.
Không chỉnh sửa raw để làm số đếm khớp kỳ vọng. Data check dùng dấu x Mẫu LLM/Nhãn tay để đếm
1.000/100, không chạy API hoặc lấy cỡ mẫu từ pipeline.

## Samples và đầu ra

- `samples/demo/`: fixture giả bốn mốc, chỉ dùng test/demo; không dùng số liệu trong bài nộp.
- `samples/manual_labels.csv`: hiện chỉ header `review_id,sentiment`, chờ 100 nhãn thật theo workbook.
  Giá trị nhãn là positive/mixed/negative; dấu x trong workbook chưa phải sentiment.
- `processed/demo/` và `processed/real/`: output do pipeline sinh, mặc định gitignore.
- `reports/checks/`: thống kê/chẩn đoán data check nhỏ được bàn giao qua PR.
- `reports/generated/real/`, `figures/real/`: báo cáo thống kê/hình phân tích tự sinh, gitignore.

Chỉ commit bảng sạch nhỏ dưới 50 MB sau khi nhóm trưởng kiểm tra. Dùng `git add -f` đúng file,
không bỏ ignore cả folder. Lệnh tái lập và số liệu chính nằm trong PR/phần báo cáo;
không dùng ảnh terminal thay file kết quả. [README nhóm](../README.md) ·
[Luồng data check](../docs/DATA_CHECK_WORKFLOW.md).
