# Hợp đồng dữ liệu và hàm

Các hàm dưới đây là interface thống nhất: QA/EDA đã có implementation, nhiều module khác
còn TODO/cần sửa theo checklist ngày 15/11. Đừng đổi chữ ký/cột ngầm.
TV1 đã triển khai analysis/viz_market và runner độc lập; READY chờ peer review, không còn stub.
`data_check.py` là luồng đã hoàn thành và độc lập; file này mô tả pipeline phân tích cả kỳ.

## Input chung

`io.rows(path)` trả iterator dict[str,str]. `loading.snapshot_rows` đọc streaming và lọc theo
assignment; listings được thêm analysis_area. ID luôn str; raw không bị sửa.
Config `.yaml` dùng cú pháp JSON, path tính từ gốc repo. Assignment chứa workbook của đúng lớp/nhóm.
Mỗi bảng records là list[dict] trừ raw iterator; cfg là dict, root/figures là Path.

## API theo owner

| Owner | Hàm | Trả về |
|---|---|---|
| Đức | qa.clean_listings(records, snapshot, cfg) | (cleaned listings, QA report) |
| Đức | eda.profile(listings) | EDA rows |
| Hiếu | kpi.summarize(listings, cfg) | listing/host/price KPI rows |
| Nam | calendar.aggregate(records, snapshot, window_days, listing_ids) | (calendar summary, issue_counts dict) |
| Nam | calendar.metrics(calendar, listings, cfg) | calendar KPI rows |
| Phan Huy | reviews.collect(records, snapshot, existing) | cập nhật review map; trả issue_counts dict |
| Phan Huy | baseline.predict(review) | review_id, sentiment, source |
| Phan Huy | llm.analyze(reviews, cfg, root, review_ids) | structured predictions đúng mẫu được giao |
| Phan Huy | llm.validate(obj, aspects) | JSON hợp lệ hoặc ValueError |
| Phan Huy | evaluate.evaluate(predictions, labels, source) | metrics rows trên cặp dự đoán/nhãn |
| Phan Huy | review_kpi.guest_kpi(predictions, listings, cfg) | guest KPI rows |
| Nhóm trưởng | analysis.churn(listings, snapshots) | hiện diện và thay đổi thuộc tính trên cặp listing, không phải entry/exit toàn Toronto |
| Nhóm trưởng | analysis.cohort_summary(listings, snapshots, expected_ids=None) | coverage/host quan sát theo mốc; mẫu số phân công nếu truyền expected_ids |
| Mỗi owner | viz_<owner>.render(tables, figures, cfg) | lưu hình, trả list[Path] |

## Schema tối thiểu

Các cột bắt buộc để pipeline chung xuất CSV; thêm cột thì cập nhật writer/contract và review.

- Listings: snapshot_date, listing_id, host_id, price, room_type, analysis_area,
  neighbourhood_cleansed, latitude, longitude, qa_flags. ID str; numeric float/None; flags nối `|`.
- QA: snapshot_date, rule, affected_rows, action, rows_after, median_price_before, median_price_after.
- EDA: snapshot_date, qa_flags, count.
- Calendar: snapshot_date, listing_id, available_days, observed_days, expected_days, availability_rate.
- Calendar KPI: snapshot_date, analysis_area, availability_rate, observed_days, expected_days, listing_n.
- Market KPI: snapshot_date, analysis_area, supply, median_price, price_n, currency,
  entire_home_share, multi_listing_host_share. Giá ngoài mốc cuối để trống.
- Cohort summary: snapshot_date, cohort_basis, cohort_size, observed_listings, missing_listings,
  coverage, observed_hosts, host_id_unusable, room_type_missing. cohort_basis = assignment khi
  expected_ids được truyền, nếu không là observed_union và không coi là mẫu số workbook.
- Churn (alias legacy): previous_snapshot, snapshot_date, previous_n, current_n, new, retained,
  disappeared, entry_rate, exit_rate, host_comparable, host_changed, host_change_rate,
  host_pairs_excluded, room_type_comparable, room_type_changed, room_type_change_rate,
  room_type_pairs_excluded. entry_rate=new/current_n, exit_rate=disappeared/previous_n chỉ mô tả
  hiện diện trong input. Host change=host_changed/host_comparable trên retained có host ID
  hợp lệ cả hai mốc; room change tương tự với giá trị không rỗng. Mẫu số 0 → None/CSV trống.
  Không suy ra gia nhập/rời Toronto hoặc chuyển quyền sở hữu từ các cột legacy này.
- Reviews: review_id, listing_id, date, comments, first_seen_snapshot; review_id duy nhất sau preprocessing.
- Baseline: review_id, sentiment, source.
- LLM: review_id, sentiment, language, positive_aspects, negative_aspects, source.
  Sentiment positive/mixed/negative; aspect arrays theo taxonomy; pipeline serialize array sang JSON trong CSV.
- Guest KPI: metric, value, sample_n, source, scope; nếu thêm breakdown, thống nhất writer.
- Evaluation: source, paired_n, manual_n, accuracy, macro_f1, meets_100_paired.
- Manual labels: review_id, sentiment. Đủ nhãn thật của 100 ID được đánh dấu trong workbook.
  Phiếu cá nhân ở data/samples/labeling/tvN.json, quy trình trong MANUAL_LABELING.md;
  CSV cuối chỉ được ghép sau khi người đọc chốt nhãn. Text 100 review phải khớp phiên bản phiếu.

Danh sách tables truyền vào viz: listings, calendar, reviews, qa_report, eda, market_kpi,
calendar_kpi, cohort_summary, churn_kpi, baseline, llm_reviews, guest_kpi, evaluation.
Không dùng stdout làm dữ liệu trả về, không tự gọi pipeline từ module, không có API/download side effect khi import.

## Khóa và quy tắc

Listings: snapshot_date + listing_id; calendar: snapshot_date + listing_id + date trước aggregate;
review_id dedupe toàn bộ mốc cho phân tích. Data check vẫn đếm riêng từng mốc trước cleaning.
analysis_area là 8 hình chữ nhật của workbook; không gọi là neighbourhood hành chính.
Không suy rộng market supply/churn/host ownership từ cohort được giao.
Giá chỉ mốc cuối, calendar không dùng giá; availability không phải occupancy.
Đổi contract cần issue + review TV1 và owner downstream, sau đó cập nhật tests/writer.
