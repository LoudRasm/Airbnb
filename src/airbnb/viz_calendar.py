"""TV4 — Vũ Phạm Khánh Nam: Availability theo thời gian/vùng, không sử dụng price calendar."""

OWNER = 'TV4 — Vũ Phạm Khánh Nam'
READY = False


def render(tables, figures, cfg):
    """Đọc các bảng từ tables, lưu hình trong figures, trả list[Path].

    tables xem docs/CONTRACTS.md; figures là Path đã tạo; không sửa bảng đầu vào.
    """
    # TODO[TV4]: Availability theo thời gian/vùng, không sử dụng price calendar.
    # TODO[TV4]: Title, đơn vị CAD/tỷ lệ, legend, caption và kiểm chứng số liệu.
    raise NotImplementedError("TODO[TV4]: viz_calendar.render — Vũ Phạm Khánh Nam")
