# Báo cáo nhóm 10

[Báo cáo chính](Nhom10_InsideAirbnb_Report.pdf) có 9 trang và được tạo từ số liệu, hình của lần chạy đầy đủ. Trang cuối có thông tin và đóng góp của năm thành viên. Hai ô MSSV còn trống trong `Nhom10_InsideAirbnb_Report.tex`. Nếu thêm một trang bìa của Viện, bản nộp có 10 trang.

`checks/` lưu báo cáo kiểm tra dữ liệu đầu vào. `sections/` lưu phần bàn giao của từng thành viên. Phụ lục kỹ thuật được lưu dưới dạng nguồn LaTeX.

## Tái tạo PDF

Từ gốc repo, dùng môi trường Python theo README và cài XeLaTeX trong TeX Live:

```bash
python scripts/build_report.py --no-download
```

Bỏ `--no-download` nếu còn thiếu raw. Dùng `--skip-pipeline` nếu lần chạy đầy đủ còn khớp config, cache và nhãn tay hiện tại. Script lấy bảng và hình từ kết quả thật rồi xuất lại `Nhom10_InsideAirbnb_Report.pdf`. Ghép bìa riêng sau lần biên dịch cuối nếu dùng mẫu Viện.

Thêm `--supplement` để xuất PDF phụ lục vào `reports/generated/report/`. Phụ lục chứa bảng chi tiết, phân tích lỗi và giải thích các đoạn code quan trọng.

## Sửa bằng Overleaf

1. Sau khi chạy pipeline đầy đủ, chạy `python scripts/build_report.py --skip-pipeline --assets-only`.
2. Tải `Nhom10_InsideAirbnb_Report.tex`, `report_style.tex` và `latexmkrc` từ `reports/` lên thư mục gốc Overleaf. Chép `reports/generated/report/` vào `generated/report/` và các PDF hình trong `figures/report/` vào `figures/report/` trên Overleaf. Có thể bỏ thư mục trung gian `latex/`.
3. Chọn XeLaTeX và đặt `Nhom10_InsideAirbnb_Report.tex` làm main document. Chỉnh nội dung hoặc điền MSSV trong file này rồi biên dịch.

Bảng và hình trong `reports/generated/` và `figures/` được tạo lại từ pipeline. Nếu thay đổi dữ liệu hoặc cache, kiểm lại các nhận định trong nội dung trước khi xuất PDF.
