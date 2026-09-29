# Bài tập lớn cuối kỳ — Inside Airbnb

**Môn học:** Lập trình xử lý dữ liệu (UET.DSE2049), học kỳ 1, năm học 2026–2027.

**Đề bài chính thức:** [Bài tập lớn Inside Airbnb](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html).

Đọc đầy đủ đề bài, phân công nhóm/thành phố và thông báo trên Canvas trước khi bắt đầu. Yêu cầu, thời hạn và rubric áp dụng theo thông báo chính thức mới nhất.

Repo template ban đầu chỉ có README này. Nhóm tự xây dựng mã nguồn, cấu hình và các sản phẩm theo đề bài, đồng thời cập nhật các mục bên dưới trong quá trình làm.

## Tạo repo của nhóm

1. Một thành viên mở [airbnb-project-template](https://github.com/tiendat-aops/airbnb-project-template), chọn **Use this template → Create a new repository**.
2. Chọn **Owner: `uet-iai-notebook-labs-2026`** và **Private**. Chỉ tạo một repo cho cả nhóm.
3. Tên gợi ý: `2627-LTXLDL-Airbnb-<TenNhom>`. Ví dụ: `2627-LTXLDL-Airbnb-dse2049_7-nhom01`.
4. Cấp quyền làm việc cho các thành viên trong nhóm; bảo đảm giảng viên phụ trách có quyền truy cập.
5. Điền URL repo vào bảng đăng ký do giảng viên cung cấp.

Nếu chưa có quyền đọc template hoặc tạo repo trong org, liên hệ giảng viên.

## Thông tin nhóm

- **Mã lớp:** TODO
- **Tên/mã nhóm:** TODO
- **Thành phố được phân công:** TODO
- **Bên đặt hàng phân tích:** TODO
- **Bốn mốc dữ liệu:** TODO — theo thành phố trong đề bài.

| Họ tên | MSSV | GitHub username | Công việc phụ trách |
|---|---|---|---|
| TODO | TODO | TODO | TODO |

Thêm dòng cho đầy đủ thành viên. Mỗi thành viên cần hiểu và giải thích được toàn bộ sản phẩm của nhóm.

## Cài đặt và chạy

Nhóm thay các mục TODO bằng hướng dẫn đã kiểm thử trên bản clone mới:

- **Phiên bản Python:** TODO — ghi phiên bản cụ thể trong `.python-version`.
- **Cài môi trường và thư viện:** TODO — cung cấp lệnh cài và `requirements.txt` ghim phiên bản hoặc lockfile tương đương.
- **Cấu hình thành phố, snapshot và tham số:** TODO — ghi đường dẫn và cách điều chỉnh.
- **Biến môi trường chứa API key:** TODO — ghi tên biến và nhà cung cấp; không ghi khóa thật.
- **Một lệnh chạy toàn bộ pipeline, bao gồm LLM:** TODO.
- **Các tệp kết quả để đối chiếu:** TODO — dữ liệu xử lý, QA, KPI, kết quả LLM, hình và báo cáo.

## Lưu ý khi làm bài

- Commit và push thường xuyên từ đầu kỳ.
- Tạo `.gitignore` trước khi thêm dữ liệu hoặc khóa API: loại `data/raw/`, `.venv/`, `.env` và mọi tệp chứa khóa thật.
- Tạo và cập nhật `AI_USAGE.md` ở gốc repo theo yêu cầu minh bạch AI trong đề bài.
- Mã nguồn phải đọc khóa API từ biến môi trường để giảng viên có thể chạy lại bằng khóa riêng.
- Tự kiểm tra bằng cách clone repo sang thư mục mới, cài môi trường theo README và chạy lại toàn bộ pipeline.

## Nộp bài

Sau khi hoàn tất sản phẩm, cập nhật báo cáo và đẩy commit cuối lên GitHub, tạo tag theo đề bài:

```bash
git tag final
git push origin final
```

Ghi commit SHA được nộp vào báo cáo. Thời hạn, cách đăng ký và lịch vấn đáp xem tại đề bài và Canvas.
