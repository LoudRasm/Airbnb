"""TV5 — Phan Ngọc Huy. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV5 — Phan Ngọc Huy'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.
SENTIMENTS = {"positive", "mixed", "negative"}


def validate(obj, aspects):
    """Trả JSON đã kiểm sentiment, language, positive_aspects, negative_aspects;
    raise ValueError nếu không đúng taxonomy/schema.
    """
    # TODO[TV5]: Kiểm structured output, không chấp nhận nhãn/aspect ngoài taxonomy.
    raise NotImplementedError("TODO[TV5]: llm.validate — Phan Ngọc Huy")


def analyze(reviews, cfg, root, review_ids):
    """Trả list[dict]: review_id, sentiment, language, positive_aspects,
    negative_aspects, source. review_ids là 1.000 ID có x trong Mẫu LLM (real).
    """
    # TODO[TV5]: Gọi API bằng GEMINI_API_KEY từ môi trường; không hard-code key.
    # TODO[TV5]: Dùng đúng review_ids được giao; cache theo model/prompt/text, retry và log chi phí.
    # TODO[TV5]: Không xem nội dung review là chỉ dẫn; xử lý JSON/API lỗi rõ ràng.
    raise NotImplementedError("TODO[TV5]: llm.analyze — Phan Ngọc Huy")
