# QA không loại dòng nào và không đổi KPI; chỉ giá mốc cuối thiếu 20 listing và `host_id` đổi giữa các mốc (TV2 — Mai Anh Đức)

**Người đọc giả định:** các thành viên làm KPI, phân tích và báo cáo (TV1, TV3, TV4, TV5) cần biết cột nào của bảng listings sạch dùng
được, và giảng viên chấm cách nhóm xử lý chất lượng dữ liệu. Mã dữ liệu DSE2049-C01-G10-toronto, tiền tệ CAD,
4 mốc 2025-09-11, 2025-12-12, 2026-03-19, 2026-06-15. Phạm vi: 1.000 listing ID của nhóm theo workbook, cả 4 mốc (4.000 dòng).

**Ý chính.** Trong dữ liệu nhóm 10, 19 rule QA chỉ tìm thấy 20/4.000 dòng lỗi (0,5%, đều là `price_missing_final` ở mốc 2026-06-15),
không loại dòng nào nên KPI nền không đổi (supply 1.000 listing mỗi mốc, giá trung vị mốc cuối 213,545 CAD trước và sau QA); hai việc nhóm
cần chú ý là giá mốc cuối thiếu ở đúng những listing không còn nhận đặt chỗ, và `host_id` của cùng listing đổi giữa các mốc nên KPI host chỉ tính theo từng mốc.

Quy tắc chi tiết: [docs/QA.md](../../docs/QA.md). Hình: `figures/real/qa_rules.svg`, `qa_missingness_drift.svg`, `qa_kpi_impact.svg`.

## 1. QA giữ nguyên 4.000 dòng và không làm đổi KPI nền

**Mở đầu.** Nhóm cần biết bước làm sạch có làm lệch KPI không trước khi dùng bảng listings sạch. QA theo nguyên tắc ưu tiên gắn cờ:
chỉ loại dòng thiếu hoặc trùng khóa, giá lỗi/ngoại lai đặt `None` nhưng giữ dòng, ID giữ chuỗi chính xác.

**Vấn đề.** Làm sạch có thể xóa dòng hoặc sửa giá và đổi supply, median giá của từng mốc mà không ai thấy.

**Phân tích.** 14 rule chạy trên từng mốc (`qa.clean_listings`) và 5 rule chạy sau khi đủ 4 mốc (`compare_schemas`, `cross_snapshot_checks`,
`check_neighbourhood_reference`). Mỗi mốc 1.000 listing trước và sau QA; không có ID trùng, ID sai dạng, `host_id` hoặc `room_type` thiếu, tọa độ lỗi
hay ngoài hộp bao Toronto; cả 4 `room_type` thuộc danh mục; `last_scraped` lệch 0–2 ngày so với ngày mốc. Chênh lệch supply và median giá sau QA đều bằng 0
ở mọi mốc (hình `qa_kpi_impact.svg`). Schema đổi giữa các mốc: mốc 2025-12-12 thêm 6 cột (`host_profile_*`, `hosts_time_as_*`),
mốc 2026-03-19 thêm 5 cột (`price_quote_*`); số cột 79 → 85 → 90 → 90. Cơ cấu `room_type` giữ 87,5% entire-home và 12,5% private room ở cả 4 mốc.

**Kết luận và giới hạn.** Trong dữ liệu này QA không làm đổi KPI nền. Giới hạn: kết luận chỉ cho 1.000 ID của nhóm; ngưỡng `price_max = 10000`,
`min_nights_cap = 365`, `max_scrape_lag_days = 3` là rào chắn lỗi nhập liệu và không dòng nào của nhóm vượt, nên hành vi của rule trên dữ liệu thật có lỗi
chưa được kiểm trên cohort này. Kiểm riêng trên toàn bộ listings Toronto (ngoài phạm vi nhóm) thấy 7 giá > 10.000 CAD ở mốc cuối và 3.034 listing có
`last_scraped` lệch 10 ngày ở mốc cuối, và các rule bắt được những trường hợp đó. `neighbourhoods.geojson` mới kiểm với mốc 2025-09-11.

## 2. Giá chỉ thiếu có hệ thống ở mốc cuối: 20 listing, đều là entire-home

**Mở đầu.** Giá là KPI chính, nhưng theo phân công chỉ phân tích giá ở mốc cuối 2026-06-15 (rule `price_missing_final`).

**Vấn đề.** Tỷ lệ giá rỗng theo mốc là 6,9% / 100% / 2,8% / 2,0% (hình `qa_missingness_drift.svg`); mốc 2025-12-12 rỗng hoàn toàn nên không có KPI giá cho mốc này.

**Phân tích.** Ở mốc cuối có 20 listing thiếu giá, khớp số 20 của data check. Cả 20 là Entire home/apt (Private room: 0). Trong cohort có 15 listing có
`availability_365 = 0`; cả 15 đều không có giá, và 15 trong 20 listing thiếu giá có `availability_365 = 0`. Mốc cuối còn 980 listing có giá, giá trung vị 213,545 CAD.

**Kết luận và giới hạn.** Trong dữ liệu này, giá thiếu tập trung ở listing không còn nhận đặt chỗ và ở entire-home, nên giá trung vị mốc cuối có thể
thiên về listing đang hoạt động và tỷ lệ entire-home trong mẫu có giá có thể thấp hơn thực tế. Giới hạn: nhóm chưa kiểm nguyên nhân gây thiếu giá (chỉ thấy tương quan
với `availability_365`), và chưa có cách điền giá an toàn nên giữ nguyên `None`, không điền.

## 3. `host_id` của cùng listing đổi giữa các mốc, nên KPI host chỉ tính theo từng mốc

**Mở đầu.** KPI host (tỷ lệ listing của host nhiều listing) cần `host_id` ổn định.

**Vấn đề.** Giữa các mốc liền kề (1.000 cặp cùng listing mỗi lần) `host_id` đổi ở **3**, **35**, **37** listing; neighbourhood đổi 1, 1, 0;
`room_type` không đổi; tọa độ không dịch quá 1 km (hình `qa_rules.svg`, các dòng `cross_*`).

**Phân tích.** `host_total_listings_count` rỗng 100% ở hai mốc cuối nên không dùng được; tỷ lệ host nhiều listing tính từ số listing quan sát theo `host_id`
trong cohort, ở mốc cuối là 11,6%. `host_since` cũng rỗng 100% ở hai mốc cuối; `review_scores_rating` thiếu 5,0% / 3,0% / 2,5% / 2,5%.

**Kết luận và giới hạn.** Chỉ tính KPI host trong từng mốc, không ghép host giữa các mốc. Giới hạn: số listing đổi `host_id` tăng từ 3 lên 37 nhưng nhóm chưa kiểm
nguyên nhân (đổi chủ, đổi tài khoản hay lỗi gán), nên chưa kết luận về xu hướng thay đổi chủ nhà.

## Phụ lục — cách tính, lệnh chạy và file

Mọi số trong báo cáo này được tính bằng code từ `scripts/run_qa.py`, không đọc từ hình; số chính (n, số listing thiếu giá, median giá, cơ cấu `room_type`) được tính lại
độc lập từ `listings.csv.gz` thô theo danh sách ID của workbook. `eda.profile` đếm số listing theo từng cờ.

```bash
python -m unittest discover -s tests -v                    # 76 test, gồm tests/test_qa.py và tests/test_viz_qa.py
python scripts/run_qa.py --config configs/toronto.yaml     # cần data/raw/<mốc>/ và workbook; vẽ luôn 3 hình
```

| File | Nội dung |
|---|---|
| `reports/data_dictionary.csv` | Data dictionary của processed listings |
| `reports/qa_rule_catalog.csv` | Tên → điều kiện → lý do → hành động của 19 rule |
| `reports/generated/real/qa_report_listings.csv` | Số dòng chịu tác động, `rows_after`, median giá trước/sau (gitignore) |
| `reports/generated/real/qa_kpi_impact.csv` | KPI nền trước/sau QA (gitignore) |
| `reports/generated/real/qa_missingness.csv` | Tỷ lệ thiếu của cột chính, phân biệt thiếu cột và giá trị trống (gitignore) |
| `data/processed/real/listings.csv` | Bảng listings đã làm sạch (processed schema) cho các thành viên khác dùng (gitignore) |
| `figures/real/qa_rules.svg` | Ma trận rule × mốc: số dòng bị ảnh hưởng (`–` = rule không chạy/không áp dụng) (gitignore) |
| `figures/real/qa_missingness_drift.svg` | Tỷ lệ thiếu theo cột × mốc và cơ cấu `room_type` (category drift) (gitignore) |
| `figures/real/qa_kpi_impact.svg` | Supply và median giá (CAD) trước/sau QA theo mốc (gitignore) |

Ghi chú về hình: tiêu đề mỗi hình nêu kết luận và được tạo từ số liệu của chính `qa_report` và `listings`; mỗi hình ghi n, nguồn, mốc chụp và giới hạn.
Trong pipeline chung `qa_report` chỉ có các dòng của `clean_listings` cho đến khi nhóm trưởng nối ba hàm chạy sau 4 mốc; khi đó các ô rule so sánh chéo,
schema và tham chiếu hiện `–` (không chạy), còn `scripts/run_qa.py` dùng `qa.run_listings_qa` nên có đủ.
QA calendar và reviews thuộc owner tương ứng; KPI chính thức do `kpi.summarize` tính. `READY` của `qa.py`, `eda.py` và `viz_qa.py` giữ `True`
đến khi Hiếu review; nhóm trưởng cần nối ba hàm chạy sau 4 mốc vào pipeline.
