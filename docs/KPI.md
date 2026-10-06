# KPI dự kiến

Stakeholder: theo dõi thị trường lưu trú Toronto; giá CAD, không quy đổi tiền.

| KPI | Công thức | Đơn vị / giới hạn |
|---|---|---|
| Observed supply | số listing ID duy nhất/snapshot | listing; không chứng minh hoạt động |
| Median price | median giá hợp lệ trong nhóm | CAD/đêm; price_n được xuất |
| Entire-home share | entire home/apt / listings | tỷ lệ 0–1 |
| Multi-listing host share | listings của host có >1 listing cùng snapshot / listings có host | tỷ lệ 0–1; dựa trên dữ liệu quan sát |
| Availability 90d | tổng ngày t / tổng ngày t,f quan sát trong window | tỷ lệ; coverage là observed/expected với listing có calendar |
| Entry/exit | new/current supply; disappeared/previous supply | tỷ lệ; retained và counts xuất cùng |
| Guest issue rate | sampled mixed+negative / sampled reviews | tỷ lệ mẫu LLM; không suy rộng population |

Market KPI có snapshot và neighbourhood breakdown; churn theo thời gian.
Guest KPI starter ở toàn mẫu review dedupe; TV5 bổ sung theo thời gian/area bằng join
review_date và listing snapshot thích hợp, ghi rõ định nghĩa. Không nhân review lặp theo snapshot.
Backlog: breakdown room_type, confidence intervals, coverage trên toàn bộ listing,
200 manual labels, aspect metrics, 6–8 final figures và diễn giải phát hiện từ dữ liệu thật.
