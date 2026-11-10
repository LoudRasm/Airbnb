"""TV1 — Dương Nhật Huy. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV1 — Dương Nhật Huy'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def churn(listings, snapshots):
    """Trả list[dict]: previous_snapshot, snapshot_date, new, retained, disappeared,
    entry_rate, exit_rate; hoặc đề xuất contract khác sau review.
    """
    # TODO[TV1]: Thiết kế market evolution cho phạm vi được giao.
    # TODO[TV1]: Danh sách cố định 1.000 ID không đo được entry/exit toàn thị trường.
    # TODO[TV1]: Kiểm chứng ý nghĩa chỉ số và giải thích giới hạn trước khi tính.
    raise NotImplementedError("TODO[TV1]: analysis.churn — Dương Nhật Huy")
