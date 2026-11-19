# Báo cáo nhóm 10

Bản chính: `Nhom10_InsideAirbnb_Report.pdf` (9 trang, gồm một trang thông tin nhóm).
Supplement: `Nhom10_InsideAirbnb_Supplement.pdf` (tệp riêng cho bảng chi tiết, phân tích lỗi và giải thích code).
Mỗi người đóng góp 20% theo yêu cầu nhóm trưởng; MSSV để trống cho nhóm tự điền ở trang cuối.
Chèn bìa một trang theo mẫu viện sẽ đưa PDF chính lên 10 trang; không gộp supplement vào PDF chính.

Bản này dùng dữ liệu thật từ pipeline đầy đủ, 1.000 kết quả Gemini trong cache và cùng 100 nhãn tay cho hai phương pháp.
Mốc thứ hai là 2025-12-12, đã được nhóm trưởng xác nhận với giảng viên. Các phiếu/CSV nhãn tay, workbook và raw không bị sửa.
Các bản ghi bàn giao trong `sections/` được giữ làm lịch sử; nội dung báo cáo chính đã được đối chiếu lại bằng kết quả mới.

## Tái tạo

Sau khi cài Python dependencies theo README gốc và có XeLaTeX/TeX Live:

```bash
python scripts/build_report.py --no-download
```

Lệnh chạy pipeline từ cache rồi tạo số liệu, hình PDF vector và biên dịch cả hai tài liệu.
Nếu raw chưa có, bỏ `--no-download` để tải theo config. Không cần key Gemini để build từ cache.

Nếu đã có lần chạy real đầy đủ khớp cache hiện tại:

```bash
python scripts/build_report.py --skip-pipeline
```

Chỉ tạo tài sản cho người biên dịch bằng Overleaf/XeLaTeX ở máy khác:

```bash
python scripts/build_report.py --skip-pipeline --assets-only
```

`reports/generated/report/` chứa values/tables LaTeX, metadata số đo, CSV lỗi và các đoạn code trích thật.
`figures/report/` chứa hình vector/PNG, sinh từ CSV và GeoJSON nguồn. Hai thư mục được gitignore vì có thể tái tạo;
không sửa tay các giá trị trong đó. Script dừng nếu những số đo chính đổi so với phần diễn giải đã kiểm chứng,
để tránh tự tạo hình mới dưới câu văn cũ. Khi thay dữ liệu/model/nhãn, cần đọc lại và sửa nội dung báo cáo.

## Chỉnh văn bản và MSSV

- Chỉnh nội dung chính và điền năm ô MSSV trong `Nhom10_InsideAirbnb_Report.tex`.
- Chỉnh nội dung kỹ thuật trong `Nhom10_InsideAirbnb_Supplement.tex`.
- `report_style.tex` giữ A4, Times New Roman/TeX Gyre Termes, cỡ 11pt và lề 2,15 cm như mẫu ban đầu.
- Gói `Nhom10_InsideAirbnb_Report_Sources.zip` chứa source và tài sản đóng băng để sửa/biên dịch trên Overleaf:
  chọn compiler XeLaTeX, main document là file Report; đổi main document sang Supplement để tạo tệp còn lại.
  Gói này không chứa raw, workbook hoặc khóa API. Muốn cập nhật số liệu, chạy script trong repo.

Mỗi hình có thông điệp, đơn vị, mẫu số và nguồn. Báo cáo không dùng số liệu minh họa để thay kết quả thật;
accuracy 96% không được coi là độ chính xác aspects/language. Ước tính chi phí dùng 679.139 review của toàn Toronto
ở mốc cuối và được ghi là gần đúng, không phải hóa đơn thực trả.
