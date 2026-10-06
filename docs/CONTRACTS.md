# Contract và dữ liệu

API module: io.rows(path) → iterator dict[str,str]; QA → (list cleaned, list report);
calendar.aggregate(iterator,snapshot,window,listing_ids) → (per-listing aggregates, issue counts);
reviews.collect(iterator,snapshot,existing) cập nhật global review map theo thứ tự ngày tăng;
kpi.summarize(listings,calendar,currency) → bảng theo snapshot + neighbourhood;
LLM analyze(reviews,cfg,root) → rows có review_id, sentiment, language, positive/negative_aspects.
Không gọi orchestration từ module; module không import run_pipeline.py.

| Bảng | Khóa | Kiểu / ý nghĩa |
|---|---|---|
| listings | snapshot_date, listing_id | ID string; price float/None CAD; flags nối bằng `|` |
| calendar_summary | snapshot_date, listing_id | int counts; rate float; cửa sổ [snapshot, snapshot+90) |
| reviews | review_id | ID string; date ISO; comments text; giữ lần thấy đầu |
| neighbourhoods | properties.neighbourhood | GeoJSON Polygon/MultiPolygon; khảo sát tên property dữ liệu thật |
| manual_labels | review_id | sentiment ∈ positive/mixed/negative, không trùng |

Listings cùng ID giữa snapshot là quan sát hợp lệ; calendar dedupe trong snapshot;
review cùng ID giữa snapshot là review lặp, collision nội dung được báo QA.
Calendar xử lý streaming nhưng tập seen lưu khóa trong cửa sổ; full Toronto cần đo RAM.
Reviews hiện giữ toàn bộ review dedupe trong RAM; chuyển SQLite/Polars khi đo thấy cần.
Download schema yêu cầu có cột khóa; gzip được đọc trọn trong pipeline (lỗi gzip sẽ làm dừng).
Source raw giữ nguyên. Flags không xóa anomaly, KPI giá loại price_outlier/invalid price.

Gia hạn contract: đề xuất issue gồm cột mới, kiểu, khóa, output example, ảnh hưởng module;
review TV1 + owner downstream trước merge. Không đổi tên cột ngầm.
Thêm snapshot chỉ sửa config và tải đúng bốn file; notebook không là dependency của pipeline.
