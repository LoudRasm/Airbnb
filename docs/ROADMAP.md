# Việc còn lại trước bài cuối

Data check đã hoàn thành; QA/EDA/KPI/LLM/hình là khung TODO. Đây là backlog, không phải
bằng chứng bài cả kỳ đã xong. [Phân công](TEAM.md) · [Triển khai](IMPLEMENTATION_GUIDE.md).

| Người | Kết quả còn phải làm |
|---|---|
| TV1 — nhóm trưởng | Chốt bên nhận phân tích; duy trì config/loader/import; thiết kế chỉ số biến động hợp lý với cohort cố định; hình tổng hợp; tích hợp PR và báo cáo |
| TV2 — Đức | Khảo sát schema và missingness; quy tắc QA/types/trùng/ngoại lai/danh mục lệch; cleaned schema, tác động QA, EDA và hình |
| TV3 — Hiếu | KPI listing/host, giá ở mốc cuối; thống nhất denominator; xử lý giới hạn neighbourhood và hình không gian |
| TV4 — Nam | Calendar streaming, availability/coverage theo cửa sổ và thời gian; kiểm trùng/ngày/available, hình thời gian; không tính giá calendar |
| TV5 — Phan Huy | Review dedupe; baseline; LLM thật với mẫu workbook, JSON/cache/retry; đánh giá cùng nhãn tay, guest KPI và hình; chi phí/phân tích lỗi |

## Thứ tự tích hợp

1. Nhóm thống nhất schema trong CONTRACTS. Đức hoàn thiện cleaned output; các bạn khác có
   thể phát triển bằng fixture đúng schema trong lúc QA chưa xong.
2. Từng owner test phần mình, viết `reports/sections/tvN.md`, mở PR; reviewer xác nhận rồi merge.
3. Phan Huy tổ chức guideline và chia 100 review được đánh dấu cho cả nhóm gán nhãn. Nếu chia
   đều là 20/người; thống nhất cách giải quyết nhãn bất đồng. Dấu x không phải nhãn sentiment.
4. Nhóm trưởng chạy các module đã tích hợp, đối chiếu CSV/hình với phần báo cáo. Chỉ bật READY
   cho module đã hoàn thành; không bỏ kiểm tra để ép pipeline chạy.
5. Chạy LLM thật, baseline và đánh giá trên cùng các review có nhãn; ghi lỗi và giới hạn.
6. Ghép báo cáo, cập nhật README/AI_USAGE, thử clone sạch với khóa môi trường khác rồi tag final.

## Quyết định cần chốt

- Bên nhận phân tích cụ thể và lý do chọn bộ KPI. Mục tiêu dự kiến trong kế hoạch cũ chưa thay
  cho quyết định cuối của nhóm.
- `neighbourhood_cleansed` thiếu: xác minh khả năng gán từ tọa độ/GeoJSON và độ bao phủ, hoặc
  thống nhất phương án với giảng viên. Không gọi vùng chữ nhật workbook là neighbourhood.
- Không diễn giải thay đổi trong 1.000 ID cố định thành listing gia nhập/rời toàn Toronto.
- Giá chỉ mốc cuối; availability không phải occupancy; mọi tỷ lệ phải ghi mẫu số/phạm vi.
- Config hiện theo workbook có mốc thứ hai 2025-12-12; trang đề ghi 2025-11-11.
  Ghi nguồn phân công và giữ nhất quán, không đổi ngày chỉ để khớp kế hoạch cũ.

## Chốt bài nộp

Đối chiếu [đề chính thức](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html)
và thông báo/workbook giảng viên: đủ QA, 5–8 KPI, hình không gian/thời gian/LLM, LLM thật,
baseline và 100 nhãn thật. Chuẩn bị `reports/report.pdf` tối đa 10 trang, nguồn/ngày/mã commit,
requirements ghim phiên bản, AI_USAGE và hướng dẫn tái lập. Hạn trong đề: 22/11/2026, tag final.

Kiểm môi trường mới, lệnh một bước, khóa API môi trường và cấu hình mốc kiểm thử khác.
Loader hiện khóa ngày theo workbook; nếu giảng viên chấm mốc khác, TV1 cần xác minh quy tắc
phân công của mốc đó và cập nhật thiết kế cùng contract/test, không tự suy ra ID hay bỏ kiểm tra.
Khả năng chạy với mốc ngoài workbook hiện chưa được xác nhận.

CI nền không kiểm API/KPI thật. Các kết quả demo/adapter AI của starter cũ không còn là chức
năng sẵn có trong các module TODO. ORIGINAL_PLAN và lịch sử Git chỉ dùng tham khảo quá trình.
