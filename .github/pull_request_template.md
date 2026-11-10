## Phần việc và kết quả

TV/người phụ trách, module/hàm đã triển khai, hành vi hoặc lỗi được xử lý.
Phân biệt data check với phân tích cả kỳ; ghi rõ phần còn TODO.

## Đầu vào / đầu ra

Phạm vi mã dữ liệu/ngày/ID; file kết quả; schema có thay đổi không.
Nếu đổi contract, nêu các module và writer/test đã cập nhật.

## Kiểm chứng

Ghi lệnh thực sự đã chạy, kết quả test, số liệu đối chiếu và đường dẫn file sinh ra.
Pipeline còn TODO của người khác thì ghi test riêng phần mình; không cần demo toàn luồng.

- [ ] Test phần mình và `python -m unittest discover -s tests -v` đạt
- [ ] Đã xem `python run_pipeline.py --status`; READY phản ánh đúng mức hoàn thành
- [ ] Không commit raw, workbook, API key hoặc output lớn/không liên quan
- [ ] Cập nhật phần báo cáo/tài liệu và AI_USAGE nếu có dùng AI

## Reviewer và giới hạn

Reviewer theo TEAM.md; ghi lỗi/giới hạn hoặc quyết định cần nhóm trưởng chốt.
Nếu bật READY, reviewer xác nhận logic và kiểm thử đã đủ trước merge.
