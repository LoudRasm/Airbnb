"""TV2 — Mai Anh Đức. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV2 — Mai Anh Đức'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def profile(listings):
    """Trả list[dict]: snapshot_date, qa_flags, count; bổ sung EDA trong file riêng nếu cần.
    """
    # TODO[TV2]: Thống kê missingness, flags và drift trên dữ liệu sau QA; không tự sửa cleaned.
    raise NotImplementedError("TODO[TV2]: eda.profile — Mai Anh Đức")
