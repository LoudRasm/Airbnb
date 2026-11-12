# Phần TV2 — QA & Preprocessing listings (Mai Anh Đức)

Mã dữ liệu DSE2049-C01-G10-toronto, tiền tệ CAD, 4 mốc 2025-09-11, 2025-12-12, 2026-03-19, 2026-06-15.
Phạm vi: 1.000 listing ID của nhóm theo workbook, cả 4 mốc (4.000 dòng). Quy tắc chi tiết: [docs/QA.md](../../docs/QA.md).

## Mục tiêu và cách xử lý

Làm sạch listings trước khi tính KPI, theo nguyên tắc ưu tiên gắn cờ. `qa.clean_listings(records, snapshot, cfg)` chạy 15 rule
trên từng mốc (thiếu, kiểu sai, trùng khóa, ngoại lai, category drift, tọa độ, ngày) và trả bảng cleaned đúng schema CONTRACTS cùng
dòng QA report. Bốn hàm chạy sau khi đã có cả 4 mốc: `compare_schemas` (schema drift), `cross_snapshot_checks` (collision giữa các mốc
liền kề), `check_neighbourhood_reference` (neighbourhood có trong geojson); `run_listings_qa` gom đúng thứ tự. Tổng 19 rule.
`eda.profile` đếm số listing theo từng cờ. Giá lỗi/ngoại lai đặt `None` nhưng giữ dòng; ID giữ chuỗi chính xác.

## Lệnh chạy và file kết quả

```bash
python -m unittest discover -s tests -v                    # 53 test, gồm tests/test_qa.py
python scripts/run_qa.py --config configs/toronto.yaml     # cần data/raw/<mốc>/ và workbook
```

| File | Nội dung |
|---|---|
| `reports/data_dictionary.csv` | Data dictionary của processed listings |
| `reports/qa_rule_catalog.csv` | Tên → điều kiện → lý do → hành động của 19 rule |
| `reports/generated/real/qa_report_listings.csv` | Số dòng chịu tác động, `rows_after`, median giá trước/sau (gitignore) |
| `reports/generated/real/qa_kpi_impact.csv` | KPI nền trước/sau QA (gitignore) |
| `reports/generated/real/qa_missingness.csv` | Tỷ lệ thiếu của cột chính, phân biệt thiếu cột và giá trị trống (gitignore) |

## Số liệu chính (chạy trên raw của nhóm)

- Không loại dòng nào: mỗi mốc 1.000 listing trước và sau QA; không có ID trùng, ID sai dạng, `host_id` hoặc `room_type` thiếu, tọa độ lỗi
  hay ngoài hộp bao Toronto; cả 4 `room_type` thuộc danh mục; mọi `neighbourhood_cleansed` có trong geojson (kiểm với geojson mốc 2025-09-11).
- Rule bắt được lỗi: `price_missing_final` = **20** listing ở mốc 2026-06-15 (khớp số 20 của data check).
- Ngày: `last_scraped` lệch 0–2 ngày so với ngày mốc, không có thứ tự ngày sai; không rule ngày nào kích hoạt.
- Schema drift: mốc 2025-12-12 thêm 6 cột (`host_profile_*`, `hosts_time_as_*`), mốc 2026-03-19 thêm 5 cột (`price_quote_*`); số cột 79 → 85 → 90 → 90.
- Collision giữa các mốc liền kề (cùng listing, 1.000 cặp mỗi lần): `host_id` đổi **3**, **35**, **37** listing; neighbourhood đổi 1, 1, 0; `room_type` không đổi;
  tọa độ không dịch quá 1 km.
- Thiếu theo cột: `price` 6,9% / 100% / 2,8% / 2,0% theo từng mốc; `host_since` và `host_total_listings_count` rỗng 100% ở hai mốc cuối;
  `review_scores_rating` 5,0% / 3,0% / 2,5% / 2,5%.
- Tác động lên KPI: **không đổi** (delta = 0) ở mọi mốc vì QA không loại dòng và không đặt lại giá nào. Mốc cuối: 980 listing có giá, giá trung vị 213,545 CAD,
  entire-home 87,5%, listing của host nhiều listing trong cohort 11,6%.

## Phát hiện

1. **Giá thiếu ở mốc cuối không ngẫu nhiên.** Cả 15 listing có `availability_365 = 0` đều thiếu giá; 15 trong 20 listing thiếu giá có `availability_365 = 0`; cả 20 là Entire home/apt.
   Giá trung vị mốc cuối vì vậy chỉ phản ánh listing còn nhận đặt chỗ, và tỷ lệ entire-home trong mẫu có giá thấp hơn thực tế.
2. **`host_id` của cùng listing đổi giữa các mốc** (3, 35, 37). Tỷ lệ host nhiều listing chỉ nên tính theo `host_id` trong từng mốc, không ghép host giữa các mốc.
3. **Không dùng `host_total_listings_count`** cho KPI host: rỗng 100% ở hai mốc cuối. Tỷ lệ host nhiều listing tính từ số listing quan sát theo `host_id` trong cohort.
4. Giá 2025-12-12 rỗng hoàn toàn nên không có KPI giá cho mốc này; theo phân công, giá chỉ phân tích ở mốc cuối nên không ảnh hưởng kết luận.

## Giới hạn

- Kết luận chỉ cho 1.000 ID của nhóm, không suy ra toàn thị trường Toronto.
- Ngưỡng `price_max = 10000`, `min_nights_cap = 365`, `max_scrape_lag_days = 3` là rào chắn lỗi nhập liệu; không dòng nào của nhóm vượt, nên chưa kiểm được hành vi của rule trên dữ liệu thật có lỗi.
  Kiểm riêng trên toàn bộ listings Toronto (ngoài phạm vi nhóm) thấy 7 giá > 10.000 CAD ở mốc cuối và 3.034 listing có `last_scraped` lệch 10 ngày ở mốc cuối; các rule bắt được các trường hợp này.
- `neighbourhoods.geojson` mới kiểm với mốc 2025-09-11; cần chạy lại với geojson từng mốc khi có đủ.
- QA calendar và reviews thuộc owner tương ứng; KPI chính thức do `kpi.summarize` tính.
- Chưa làm `viz_qa.render` (hình QA, tùy chọn theo đề). `READY` giữ `False` đến khi Hiếu review và nhóm trưởng nối ba hàm chạy sau 4 mốc vào pipeline.
