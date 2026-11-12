"""TV3 — Nguyễn Quốc Hiếu. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

OWNER = 'TV3 — Nguyễn Quốc Hiếu'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.


def summarize(listings, cfg):
    """Trả list[dict]: snapshot_date, analysis_area, supply, median_price, price_n,
    currency, entire_home_share, multi_listing_host_share. Giá ngoài mốc cuối để trống.
    """
    # TODO[TV3]: Tính giá chỉ mốc cuối, room type và host; ghi rõ công thức/denominator.
    # TODO[TV3]: Nhận analysis_area từ workbook; phân biệt vùng phân tích với neighbourhood.
    # TODO[TV3]: Không tự tính availability/guest KPI ở đây; Nam/Phan Huy sở hữu phần đó.
    # TODO[TV3]: Các KPI phản ánh 1.000 ID được giao, không suy rộng toàn Toronto.
    raise NotImplementedError("TODO[TV3]: kpi.summarize — Nguyễn Quốc Hiếu")
