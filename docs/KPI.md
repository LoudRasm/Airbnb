# KPI dự kiến — chưa triển khai

Hiếu/Nam/Phan Huy và nhóm trưởng triển khai theo TEAM.md. Nhóm phải chốt bên nhận phân tích
cụ thể và lý do chọn KPI; bảng này là đề xuất, không phải số liệu đã có.
[Hợp đồng hàm/bảng](CONTRACTS.md) · [Việc còn lại](ROADMAP.md).

| KPI đề xuất | Cách tính dự kiến | Owner / phạm vi |
|---|---|---|
| Listing quan sát | Listing ID duy nhất sau QA trong mỗi mốc | Hiếu; cohort được giao, không phải toàn Toronto |
| Giá trung vị | Median giá hợp lệ, kèm số listing có giá | Hiếu; chỉ mốc cuối, CAD/đêm |
| Tỷ lệ entire-home | Entire home/apt / listing có loại phòng hợp lệ | Hiếu; chốt mẫu số với QA |
| Tỷ lệ listing của host nhiều chỗ ở | Listing thuộc host có >1 listing quan sát / listing có host hợp lệ | Hiếu; không suy ra toàn bộ tài sản của host |
| Availability | Ngày available=t / ngày quan sát hợp lệ t,f trong cửa sổ | Nam; theo mốc/vùng, kèm observed/expected và coverage |
| Cảm xúc mixed/negative | Review mẫu LLM có nhãn mixed hoặc negative / review mẫu có dự đoán hợp lệ | Phan Huy; không suy rộng toàn bộ khách hàng |
| Thay đổi trong cohort | Chỉ số biến động quan sát được sau khi xác minh ý nghĩa | TV1; contract churn hiện cần xem xét lại |

Công thức/mẫu số trên phải thống nhất với source và CONTRACTS trước merge. Ghi tên, mục tiêu,
công thức, đơn vị, cách xử lý missing và phạm vi mẫu trong phần báo cáo; không chỉ xuất con số.
Có thể thay KPI dự kiến nếu có lý do, đồng thời cập nhật writer/tests và tài liệu.

`kpi_market` hiện theo `analysis_area`; đây là tám vùng chữ nhật workbook. Nó chưa chứng minh
đạt yêu cầu KPI theo `neighbourhood_cleansed`. Hiếu/TV1 xác minh khả năng gán từ tọa độ/GeoJSON,
báo unmatched/coverage, hoặc thống nhất phương án với giảng viên. Không đổi tên vùng để coi đạt.

Reviews được giao độc lập với listing IDs; KPI cần join phải kiểm độ bao phủ và không loại
reviews trước bước LLM chỉ vì listing nằm ngoài cohort. Dedupe review giữa mốc cho phân tích,
nhưng data check vẫn đếm riêng từng mốc. Baseline/LLM đánh giá trên cùng các review có nhãn thật.

Churn/entry/exit dựa trên 1.000 ID cố định không mô tả listing gia nhập/rời thị trường Toronto.
Unavailable không đồng nghĩa booked/occupancy. Calendar không có giá; không làm weekend pricing.
Phần giá ở các mốc trước để trống theo contract. Chỉ số thời gian và không gian do owner bổ sung
với mẫu số rõ ràng; hình sinh trong viz riêng và dùng số liệu cùng pipeline.
