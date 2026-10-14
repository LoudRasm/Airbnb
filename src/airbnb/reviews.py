"""TV5 — Phan Ngọc Huy. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV5 — Phan Ngọc Huy'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def collect(records, snapshot, existing):
    """records: iterator reviews đã lọc bằng review_id.
    Cập nhật existing: review_id -> {review_id, listing_id, date, comments, first_seen_snapshot}.
    Trả dict issue_name -> số dòng.
    """
    # TODO[TV5]: Dedupe theo review_id giữa mốc cho phân tích; báo collision.
    # TODO[TV5]: Giữ comments và ID chính xác; không lọc thêm theo listing_id.
    # TODO[TV5]: Không thay logic data_check: báo cáo đầu vào vẫn đếm từng mốc riêng.
    raise NotImplementedError("TODO[TV5]: reviews.collect — Phan Ngọc Huy")
