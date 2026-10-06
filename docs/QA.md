# QA starter và phần cần phát triển

| Rule | Điều kiện | Lý do | Hành động |
|---|---|---|---|
| missing_id | ID trống | không định danh | loại khỏi cleaned |
| duplicate_listing | ID lặp trong snapshot | tránh đếm đôi | giữ dòng đầu |
| invalid_price | không parse / không hữu hạn | KPI giá cần numeric | None + flag |
| price_outlier | <=0 hoặc >qa.price_max | giá bất thường | flag, không tính median |
| category_drift | room_type ngoài config | schema/category thay đổi | flag |
| missing_area/host | trống | không breakdown/host metric được | flag; host trống không vào denominator |
| invalid_minimum_nights | thiếu/<1/>cap | lưu trú bất thường | flag |
| calendar invalid date/available | không parse / không t,f | aggregate sai | bỏ khỏi aggregate |
| orphan_calendar | không có listing cleaned | join không hợp lệ | loại aggregate |
| duplicate_calendar | cùng listing,date trong snapshot | đếm đôi | giữ dòng đầu |
| invalid_review | thiếu ID/text/date, date sau snapshot | không thể phân tích | loại |
| duplicate_review | ID đã thấy | review tích lũy | giữ lần thấy đầu |
| review_collision | cùng ID, khác nội dung/listing/date | collision | báo count, giữ lần đầu |

qa_report.csv có affected_rows, rows_after và median price trước/sau cho listings.
Những rule khác chưa có KPI impact đầy đủ; không xem starter là hoàn thành rubric.
Ngưỡng 10,000 CAD là **giả định khung**, nhóm phải khảo sát/phê duyệt và giải thích.
Backlog: geographic bounds, schema drift giữa mốc, room type drift theo tỷ lệ,
review orphan, coverage thiếu calendar, QA provenance chi tiết, KPI impact của từng rule.
