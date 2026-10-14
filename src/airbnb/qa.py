"""TV2 — Mai Anh Đức. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV2 — Mai Anh Đức'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def clean_listings(records, snapshot, cfg):
    """records: iterator raw listings đã lọc ID, có analysis_area.
    Trả (cleaned_rows, qa_report_rows), không sửa raw.
    cleaned: snapshot_date, listing_id/host_id dạng str, price float/None,
    room_type, analysis_area, neighbourhood_cleansed, latitude, longitude, qa_flags.
    QA report: snapshot_date, rule, affected_rows, action, rows_after,
    median_price_before, median_price_after.
    """
    # TODO[TV2]: Khảo sát schema/type, missing, duplicate, outlier, category/schema drift.
    # TODO[TV2]: Ưu tiên flag; giá rỗng trước mốc cuối không phải lỗi xin cấp lại.
    # TODO[TV2]: Giữ ID chính xác, lập dictionary/rule và kiểm KPI trước/sau QA.
    raise NotImplementedError("TODO[TV2]: qa.clean_listings — Mai Anh Đức")
