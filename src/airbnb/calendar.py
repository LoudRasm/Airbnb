"""TV4 — Vũ Phạm Khánh Nam. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV4 — Vũ Phạm Khánh Nam'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def aggregate(records, snapshot, window_days, listing_ids):
    """Nhận iterator calendar đã lọc; trả (summary_rows, issue_counts).
    summary: snapshot_date, listing_id, available_days, observed_days,
    expected_days, availability_rate. issue_counts là dict rule -> số dòng.
    """
    # TODO[TV4]: Xử lý streaming, cửa sổ [snapshot, snapshot + window_days).
    # TODO[TV4]: Kiểm ngày, available, duplicate, coverage; không dùng giá calendar.
    # TODO[TV4]: Không gọi unavailable là booked/occupancy.
    raise NotImplementedError("TODO[TV4]: calendar.aggregate — Vũ Phạm Khánh Nam")


def metrics(calendar, listings, cfg):
    """Trả list[dict]: snapshot_date, analysis_area, availability_rate,
    observed_days, expected_days, listing_n, currency nếu có chỉ số tiền tệ.
    """
    # TODO[TV4]: Aggregate availability theo vùng và thời gian, báo denominator/coverage.
    # TODO[TV4]: Thêm 30/90 ngày và temporal supporting metrics vào hàm riêng nếu cần.
    raise NotImplementedError("TODO[TV4]: calendar.metrics — Vũ Phạm Khánh Nam")
