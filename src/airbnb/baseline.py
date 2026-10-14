"""TV5 — Phan Ngọc Huy. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV5 — Phan Ngọc Huy'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def predict(review):
    """Trả dict tối thiểu review_id, sentiment, source; thêm aspect/language nếu đối chứng.
    """
    # TODO[TV5]: Thiết kế đối chứng không LLM và kiểm chứng; không gán positive mặc định.
    # TODO[TV5]: Giải thích giới hạn ngôn ngữ và so sánh trên cùng bộ nhãn tay.
    raise NotImplementedError("TODO[TV5]: baseline.predict — Phan Ngọc Huy")
