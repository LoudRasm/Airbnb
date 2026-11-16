# Kế hoạch QA — Đức phụ trách

Module phân tích hiện là TODO; các quy tắc dưới là đề xuất để Đức khảo sát, kiểm chứng và
triển khai. Data check đã hoàn thành vẫn giữ nguyên và đếm dữ liệu trước cleaning.
[Hướng dẫn triển khai](IMPLEMENTATION_GUIDE.md) · [Schema](CONTRACTS.md).

Mỗi quy tắc cần ghi điều kiện, lý do, hành động và tác động số liệu. Ưu tiên gắn cờ; việc loại
bỏ/dedupe hoặc chọn dòng phải có lý do và test. Không dùng quy tắc dự kiến như kết quả đã chạy.

| Nhóm kiểm tra | Đề xuất | Người triển khai |
|---|---|---|
| Thiếu | ID/host/vùng/giá/text thiếu; phân biệt thiếu cột với giá trị trống | Đức: listings; Nam: calendar; Phan Huy: reviews |
| Kiểu sai | ID chuỗi chính xác; số/ngày parse đúng, hữu hạn; available t/f | Theo owner từng bảng |
| Trùng | Khóa trong mốc và bản ghi giữa mốc; quy tắc chọn dòng và collision | Theo owner từng bảng |
| Ngoại lai | Giá mốc cuối, minimum_nights, tọa độ; khảo sát ngưỡng và ảnh hưởng | Đức phối hợp Hiếu |
| Danh mục/schema lệch | Room type ngoài danh mục và cột/kiểu thay đổi giữa mốc | Đức |
| Bao phủ/join | Calendar thiếu ngày, review không ghép được listing, vùng không xác định | Nam/Hiếu/Phan Huy phối hợp Đức |

`qa.clean_listings` trả cleaned schema và QA report; calendar/reviews trả issue counts theo
CONTRACTS. Nhóm trưởng gom thành `reports/qa_report.csv`; thống nhất tên rule để tránh trùng.
Bảng có snapshot, rule, affected_rows, action, rows_after, median_price_before/after.
Đức cần giải thích tác động lên KPI và bổ sung contract nếu các KPI khác cần trường riêng.

Giá chỉ phân tích ở mốc cuối; thiếu giá các mốc trước không phải lỗi cần xin dữ liệu khác.
Ngưỡng `qa.price_max = 10000` CAD và `min_nights_cap = 365` là tham số khung, chưa được khảo
sát; chỉ dùng sau khi giải thích lựa chọn. Calendar không kiểm/tính giá.
`neighbourhood_cleansed` thiếu không được điền bằng mã vùng chữ nhật rồi gọi là neighbourhood.
ID không qua float; raw/workbook không bị sửa; review filter độc lập listing_id.

Đức bổ sung từ điển dữ liệu, quy tắc đã chọn, số dòng/KPI trước và sau QA vào docs/phần báo cáo.
Tests cần có trường hợp lỗi thật được mô phỏng và kết quả kỳ vọng có lý do; hình QA do
`viz_qa.py` sinh. Đọc output CSV để kiểm số liệu, không chỉ nhìn terminal hoặc CI xanh.

---

## Triển khai của Đức (cập nhật 22/10/2026)

Phần phía trên là kế hoạch ban đầu của nhóm, giữ nguyên. Phần dưới là kết quả đã triển khai và kiểm chứng; khi hai phần khác nhau (ví dụ ngưỡng "chưa khảo sát") thì lấy phần dưới.

Tài liệu mô tả phần QA & preprocessing **đã triển khai** trong `src/airbnb/qa.py` và `src/airbnb/eda.py`.
Data check đầu vào (`scripts/check_data.py`) vẫn giữ nguyên và đếm dữ liệu **trước** cleaning.
[Schema](CONTRACTS.md) · [Phân công](TEAM.md) · [Báo cáo phần TV2](../reports/sections/tv2.md).

### Phạm vi

QA chạy trên listings đã lọc theo workbook của nhóm (1.000 ID, 4 mốc). Phần QA của calendar và reviews do
Nam và Phan Huy triển khai, trả `issue_counts` theo [CONTRACTS](CONTRACTS.md). Khóa listings là
`snapshot_date + listing_id`; cùng một listing xuất hiện ở nhiều mốc **không** phải duplicate.

### Trạng thái từng nhóm kiểm tra (phần listings của Đức)

| Nhóm kiểm tra | Rule / kết quả đã triển khai |
|---|---|
| Thiếu | `id_missing`, `critical_field_missing`, `price_missing_final`, `neighbourhood_missing`; mức độ thiếu từng cột trong `qa_missingness.csv` |
| Kiểu sai | `id_format`, `price_unparseable`, `coordinates_invalid`, `date_invalid` |
| Trùng | `duplicate_key` (trong mốc); `cross_host_id_changed`, `cross_category_changed`, `cross_coordinates_moved` (giữa các mốc) |
| Ngoại lai | `price_outlier`, `min_nights_outlier`, `coordinates_outside_city`; ngưỡng cần Hiếu xác nhận khi review |
| Danh mục/schema lệch | `room_type_unknown`, `schema_drift` |
| Bao phủ/join | Phần listings: `neighbourhood_not_in_reference`, `scrape_date_offset`; calendar/reviews do owner trả `issue_counts` |
| Hình | `viz_qa.render` → `qa_rules.svg` (rule × mốc), `qa_missingness_drift.svg` (thiếu theo cột, cơ cấu `room_type`), `qa_kpi_impact.svg` (supply, median giá trước/sau QA) |

### Cách chạy

```bash
python -m unittest discover -s tests -p test_qa.py -v   # test riêng phần QA
python scripts/run_qa.py --config configs/toronto.yaml  # chạy trên raw + workbook của nhóm
```

`run_qa.py` ghi bảng sạch `data/processed/real/listings.csv` (gitignore; pipeline chung sẽ ghi đè cùng đường dẫn),
`reports/data_dictionary.csv`, `reports/qa_rule_catalog.csv` (commit được) và, vào
`reports/generated/real/` (gitignore), `qa_report_listings.csv`, `qa_kpi_impact.csv`, `qa_missingness.csv`, cùng ba hình SVG vào
`figures/real/` (gitignore). Chạy riêng phần hình: `python -m unittest discover -s tests -p test_viz_qa.py -v`.
Pipeline chung gọi `qa.clean_listings(records, snapshot, cfg)` từng mốc; sau 4 mốc cần gọi thêm
`qa.compare_schemas`, `qa.cross_snapshot_checks` và `qa.check_neighbourhood_reference` (xem
`qa.run_listings_qa` — gom đúng thứ tự các hàm này) để các dòng tương ứng vào `reports/qa_report.csv`.

### Quy tắc (tên → điều kiện → lý do → hành động)

Nguyên tắc: ưu tiên **gắn cờ**; chỉ loại dòng khi thiếu/trùng khóa. Giá lỗi/ngoại lai đặt `None` nhưng giữ dòng.
Rule chạy tuần tự; `rows_after` và `median_price_*` trong `qa_report` là trạng thái tích lũy sau rule đó.
`raw_input` là dòng cơ sở (không tính vào 19 rule).

| Rule | Nhóm | Điều kiện | Lý do | Hành động |
|---|---|---|---|---|
| `raw_input` | Cơ sở | Mọi dòng listing đã lọc theo workbook | Mốc so sánh trước/sau; ghi cột bắt buộc bị thiếu | Không đổi dữ liệu |
| `id_missing` | Thiếu | id rỗng sau khi bỏ khoảng trắng | Không có khóa (snapshot_date, listing_id) thì không nối được các bảng | Loại dòng |
| `id_format` | Kiểu sai | id không phải toàn chữ số ASCII (vd 123.0, 1.2e+17) | Dấu hiệu ID đã đi qua float/Excel và mất chính xác | Gắn cờ, giữ nguyên chuỗi |
| `duplicate_key` | Trùng | Cùng listing_id xuất hiện nhiều lần trong một mốc | Khóa phải duy nhất; không đếm lặp supply | Giữ dòng đầu, loại dòng sau, đếm số cặp khác nội dung |
| `critical_field_missing` | Thiếu | host_id, room_type hoặc analysis_area rỗng | Cần cho KPI host nhiều listing, entire-home và theo vùng | Gắn cờ theo từng cột (host_id_missing, room_type_missing, analysis_area_missing) |
| `price_missing_final` | Thiếu | price rỗng ở mốc cuối của config | Giá chỉ phân tích ở mốc cuối; rỗng ở mốc trước không phải lỗi | Gắn cờ (không áp dụng mốc trước) |
| `price_unparseable` | Kiểu sai | price khác rỗng nhưng không đọc được thành số hữu hạn | Không thể tính median | Đặt price=None, gắn cờ |
| `price_outlier` | Ngoại lai | price <= 0 (price_nonpositive) hoặc price > qa.price_max (price_outlier_high) | Giá đêm không thể không dương; rào chắn lỗi nhập liệu cực lớn | Đặt price=None, giữ dòng, gắn cờ |
| `room_type_unknown` | Category drift | room_type khác rỗng nhưng không thuộc qa.room_types | Phát hiện danh mục mới/đổi tên giữa các mốc | Gắn cờ, giữ nguyên giá trị |
| `coordinates_invalid` | Địa lý | latitude/longitude rỗng, không phải số hữu hạn, ngoài [-90,90]/[-180,180] hoặc (0,0) | Không đặt được lên bản đồ | Đặt tọa độ=None, gắn cờ |
| `coordinates_outside_city` | Địa lý | Tọa độ hợp lệ nhưng ngoài hộp bao qa.bbox của thành phố | Nghi sai vị trí; không tự sửa | Gắn cờ (bỏ qua nếu config không có qa.bbox) |
| `neighbourhood_missing` | Thiếu | neighbourhood_cleansed rỗng | KPI neighbourhood cần cột gốc; không điền bằng analysis_area | Gắn cờ, không điền |
| `neighbourhood_not_in_reference` | Toàn vẹn tham chiếu | neighbourhood_cleansed khác rỗng nhưng không có trong neighbourhoods.geojson của mốc | Không nối được với ranh giới/bản đồ | Chỉ báo cáo số dòng (chạy sau clean_listings, không thêm cờ) |
| `min_nights_outlier` | Ngoại lai | minimum_nights > qa.min_nights_cap (mặc định 365) | Nghi giá trị nhập sai hoặc listing không cho thuê ngắn hạn | Gắn cờ |
| `date_invalid` | Ngày sai | last_scraped/host_since/first_review/last_review không phải ngày ISO (date_unparseable) hoặc first_review > last_review, last_review/host_since > last_scraped (date_order_invalid) | Ngày sai làm hỏng phân tích thời gian | Gắn cờ |
| `scrape_date_offset` | Ngày sai | \|last_scraped - snapshot_date\| > qa.max_scrape_lag_days (mặc định 3 ngày) | Dòng được thu thập lệch xa ngày mốc, ảnh hưởng so sánh theo thời gian | Gắn cờ |
| `cross_host_id_changed` | Giữa các mốc | Cùng listing_id ở hai mốc liền kề nhưng host_id khác | Collision/đổi chủ; làm sai tỷ lệ host nhiều listing nếu bỏ qua | Chỉ báo cáo số cặp |
| `cross_category_changed` | Giữa các mốc | Cùng listing_id nhưng room_type hoặc neighbourhood_cleansed khác giữa hai mốc liền kề | Đổi loại phòng/khu vực làm lệch KPI theo thời gian | Chỉ báo cáo số cặp (chi tiết room_type/neighbourhood trong cột action) |
| `cross_coordinates_moved` | Giữa các mốc | Cùng listing_id, tọa độ dịch > qa.coord_shift_km (mặc định 1 km) | Nghi sai tọa độ hoặc gộp nhầm listing | Chỉ báo cáo số cặp |
| `schema_drift` | Schema | Tập cột listings của mốc khác mốc liền trước | Cột thêm/bớt làm hỏng parser hoặc KPI | Chỉ báo cáo cột thêm/bớt |

Tham số nằm trong `configs/toronto.yaml` mục `qa`: `price_max`, `min_nights_cap`, `room_types`, `bbox`,
`max_scrape_lag_days`, `coord_shift_km`. Ngưỡng `price_max = 10000` và `min_nights_cap = 365` là rào chắn lỗi nhập liệu:
trên 1.000 listing của nhóm không dòng nào vượt (giá mốc cuối cao nhất 3.673,85 CAD; `minimum_nights` tối đa 365).
`max_scrape_lag_days = 3` chọn theo `last_scraped` quan sát được: nhóm lệch 0–2 ngày so với ngày mốc.

### Data dictionary (processed listings)

| Cột | Kiểu | Mô tả | Nguồn | Rule liên quan |
|---|---|---|---|---|
| `snapshot_date` | date | Ngày mốc (YYYY-MM-DD) theo config/workbook | config | Khóa cùng listing_id |
| `listing_id` | str | ID listing, giữ nguyên chuỗi (nhiều ID > 2^53) | listings.id | id_missing, id_format, duplicate_key |
| `host_id` | str | ID host, giữ nguyên chuỗi | listings.host_id | critical_field_missing, cross_host_id_changed |
| `price` | float|None | Giá mỗi đêm, CAD; chỉ dùng ở mốc cuối; None nếu thiếu/lỗi | listings.price | price_missing_final, price_unparseable, price_outlier |
| `room_type` | str | Loại phòng như trong nguồn (không chuẩn hóa) | listings.room_type | critical_field_missing, room_type_unknown |
| `analysis_area` | str | Vùng chữ nhật A01–A08 của workbook; không phải neighbourhood hành chính | workbook sheet Listing | critical_field_missing |
| `neighbourhood_cleansed` | str | Neighbourhood theo Inside Airbnb; không điền khi thiếu | listings.neighbourhood_cleansed | neighbourhood_missing, neighbourhood_not_in_reference |
| `latitude` | float|None | Vĩ độ WGS84; None nếu không hợp lệ | listings.latitude | coordinates_invalid, coordinates_outside_city |
| `longitude` | float|None | Kinh độ WGS84; None nếu không hợp lệ | listings.longitude | coordinates_invalid, coordinates_outside_city |
| `qa_flags` | str | Tên các cờ QA nối bằng "\|", sắp xếp; rỗng nếu không có | qa.py | tất cả rule gắn cờ |

Cờ con (tên trong `qa_flags`): `host_id_missing`, `room_type_missing`, `analysis_area_missing` (rule `critical_field_missing`),
`price_nonpositive`, `price_outlier_high` (rule `price_outlier`), `date_unparseable`, `date_order_invalid` (rule `date_invalid`).
`analysis_area` là 8 hình chữ nhật của workbook, không phải neighbourhood hành chính; `neighbourhood_cleansed` thiếu không được điền.

### Tác động QA lên KPI

`qa_kpi_impact.csv` so giá trị trước QA (raw đã parse) và sau QA cho supply, số listing có giá, giá trung vị, tỷ lệ
entire-home và tỷ lệ listing của host nhiều listing (đếm theo `host_id` trong cohort). Đây là công thức tối thiểu để đo
tác động QA; KPI chính thức do `kpi.summarize` (TV3) tính theo [KPI](KPI.md). Số liệu và diễn giải: báo cáo TV2.

### Giới hạn

- Chỉ kiểm listings; ngày/tham chiếu của calendar và reviews thuộc owner tương ứng.
- Ngưỡng chưa thử trên dữ liệu ngoài 1.000 ID của nhóm; chạy mốc khác chỉ cần sửa config nhưng phải xem lại ngưỡng.
- `check_neighbourhood_reference` cần `neighbourhoods.geojson` từng mốc; mốc thiếu file bị bỏ qua.
- Không dùng `host_total_listings_count` cho KPI host: cột này rỗng 100% ở hai mốc cuối.
