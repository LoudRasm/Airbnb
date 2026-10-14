# Câu trả lời báo cáo kiểm tra dữ liệu

Mã dữ liệu: DSE2049-C01-G10-toronto

## 1. Có tệp nào không tải hoặc đọc được không?

Đã đọc thành công đủ 12 file gốc đang lưu tại máy; không ghi nhận lỗi đọc.

## 2. Mẫu LLM và nhãn tay

Mẫu LLM: 1000 review. Nhãn tay: 100 review. Lấy trực tiếp dấu x ở hai cột trong sheet Review của workbook; không lấy từ pipeline nhóm.

## 3. Các cột listings có từ 90% giá trị thiếu trở lên

- 2025-09-11: neighbourhood_group_cleansed, calendar_updated
- 2025-12-12: neighborhood_overview, neighbourhood, neighbourhood_group_cleansed, price, calendar_updated, estimated_revenue_l365d
- 2026-03-19: neighborhood_overview, host_since, host_response_time, host_response_rate, host_acceptance_rate, host_thumbnail_url, host_neighbourhood, host_total_listings_count, neighbourhood, neighbourhood_group_cleansed, calendar_updated, instant_bookable
- 2026-06-15: neighborhood_overview, host_since, host_response_time, host_response_rate, host_acceptance_rate, host_thumbnail_url, host_neighbourhood, host_total_listings_count, neighbourhood, neighbourhood_group_cleansed, calendar_updated, instant_bookable

## 4. Cột dự định dùng nhưng bị rỗng

Chỉ sử dụng giá listings ở mốc cuối 2026-06-15; không phân tích biến động giá qua bốn mốc. Giá rỗng ở các mốc trước không phải lý do xin cấp lại. Calendar chỉ dùng cho lịch và availability, không phân tích giá.
Nhóm cần bổ sung quyết định đối với các cột khác dự định dùng sau khi xem danh sách ở câu 3.

## 5. Kết luận

Các file đọc được và số lượng kiểm soát khớp hướng dẫn. Dữ liệu đủ cho các bước kiểm tra được triển khai; nhóm trưởng cần xem lại câu 3–4 và xác nhận phạm vi phân tích trước khi nộp. Không xin cấp lại chỉ vì thiếu giá ở mốc trước.
