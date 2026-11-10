"""TV5 — Phan Ngọc Huy. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV5 — Phan Ngọc Huy'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def guest_kpi(predictions, listings, cfg):
    """Trả list[dict] chứa metric, value, sample_n, source, scope;
    bổ sung snapshot/analysis_area nếu liên kết review với listing hợp lệ.
    """
    # TODO[TV5]: Ít nhất một KPI từ LLM; denominator rõ và không nhân review qua snapshot.
    # TODO[TV5]: Làm rõ mẫu được giao, bias và giới hạn suy rộng.
    raise NotImplementedError("TODO[TV5]: review_kpi.guest_kpi — Phan Ngọc Huy")
