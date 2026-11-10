"""TV5 — Phan Ngọc Huy. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV5 — Phan Ngọc Huy'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def evaluate(predictions, labels, source):
    """Trả list[dict]: source, paired_n, manual_n, accuracy, macro_f1, meets_100_paired.
    """
    # TODO[TV5]: Chấm baseline/LLM trên cùng ID có nhãn thật; không dùng x như nhãn sentiment.
    # TODO[TV5]: Kiểm duplicate/missing labels, ít nhất 100 paired nhãn thật; phân tích lỗi.
    raise NotImplementedError("TODO[TV5]: evaluate.evaluate — Phan Ngọc Huy")
