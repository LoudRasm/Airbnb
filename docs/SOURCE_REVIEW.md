# Kết quả xử lý rà soát pipeline

Đợt rà soát bắt đầu tại main `86b609e` ngày 2026-11-16; sửa và kiểm chứng đến 2026-11-17.
Giữ lịch sử tác giả và thuật toán đúng của các thành viên; không sửa nhãn tay.
[Kiểm chứng](VERIFICATION.md) · [Dữ liệu trước/sau](../reports/data_alignment_2026-11-16.json).

| Điểm rà soát | Xử lý |
|---|---|
| Chấm không API key, cache thiếu | Pipeline cache-only; script tạo/kiểm cache riêng; ngoại lệ gitignore cho cache. **Chưa có cache thật**, nhóm đã xác nhận |
| Skip LLM ghi đè kết quả | Thư mục real/non_llm riêng; không xuất LLM/evaluation/guest rỗng vào real |
| Khóa ngày theo workbook | Giữ ID/mã nhóm; cho ngày config mới với skip-llm, full evaluation vẫn đủ mốc giao |
| GeoJSON path ghi cứng | Orchestration đọc raw theo config và truyền GeoJSON cho module vẽ |
| Runner TV5 thiếu paths.manual_labels | Dùng reader nhãn chung/config; bỏ fallback ngầm chỉ 20 nhãn/100 packet |
| QA chỉ chạy từng mốc | Tái sử dụng run_listings_qa đầy đủ, xuất missingness/impact/schema/cross/reference |
| Coverage calendar mất listing vắng | Tạo exposure đầy đủ, None khi không observed, thêm coverage và issue thiếu ngày |
| Chưa xuất neighbourhood KPI | Một công thức nhóm dùng lại cho kpi_market và kpi_neighbourhood |
| Supply bản đồ chỉ tính có giá | Đếm mọi listing; mẫu giá price_n riêng |
| Tiêu đề QA tính trùng dòng | Ghi lượt vi phạm, bỏ tỷ lệ dòng không có mẫu số duy nhất |
| CI bỏ test dạng hàm | Chuyển CI sang pytest, chạy cả test dạng hàm và unittest |
| KPI phi giá mất mốc trước | Tính theo từng snapshot; giá chỉ price_snapshot |
| Guest KPI không có listing_id join | Ghép ID từ review nguồn sau dự đoán; giữ mẫu review độc lập, báo coverage |
| PNG calendar giả khi thiếu thư viện | Dùng matplotlib thật, lỗi dependency phải được xử lý |

Dọn source: runner gốc mỏng, tách điều phối/schema/đọc nhãn; giữ module nghiệp vụ của owner.
Script data check cũ chuyển tiếp sang luồng chung thay cho đường dẫn máy cá nhân/ID ghi cứng.
Xóa bản sao dictionary/catalog trong reports/sections; giữ bản chuẩn tại reports/.
Bỏ CSV cá nhân mà notebook calendar dùng làm fallback; notebook đọc raw có scope, không âm thầm dùng dữ liệu cũ.
Các phần phân tích/biểu đồ đúng trong notebook được giữ; không dùng notebook thay pipeline.

Không có kết quả Gemini thật hoặc báo cáo PDF cuối được tạo trong đợt sửa này. Không tag final.
Chênh lệch ngày tháng 11/tháng 12 giữa đề và workbook được ghi rõ, không tự đổi dữ liệu được giao.
