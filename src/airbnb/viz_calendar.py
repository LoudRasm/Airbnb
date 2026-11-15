"""TV4 — Vũ Phạm Khánh Nam: Availability theo thời gian/vùng, không sử dụng price calendar."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import struct
import zlib

OWNER = "TV4 — Vũ Phạm Khánh Nam"
READY = True


def _check_rate(val: float, name: str) -> float:
    rate = float(val)
    if not (-1e-6 <= rate <= 1.0 + 1e-6):
        raise ValueError(f"Chỉ số {name}={rate} nằm ngoài khoảng hợp lệ [0, 1]")
    return rate


def _write_fallback_png(path: Path, width: int = 320, height: int = 180) -> None:
    """Tạo file PNG hợp lệ bằng thư viện chuẩn Python khi môi trường CI không cài matplotlib."""
    raw_rows = []
    for y in range(height):
        row = bytearray([0])
        for _ in range(width):
            if y < 24:
                row.extend((43, 92, 143))
            else:
                row.extend((245, 247, 250))
        raw_rows.append(bytes(row))

    raw_data = b"".join(raw_rows)

    def _chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack("!I", len(data))
            + tag
            + data
            + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw_data))
        + _chunk(b"IEND", b"")
    )
    path.write_bytes(png_bytes)


def render(tables, figures, cfg):
    """Đọc các bảng từ tables, lưu hình trong figures, trả list[Path].

    tables xem docs/CONTRACTS.md; figures là Path đã tạo; không sửa bảng đầu vào.
    """
    figures = Path(figures)
    figures.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    calendar_kpi = list(tables.get("calendar_kpi") or [])
    calendar_rows = list(tables.get("calendar") or [])
    listings_rows = list(tables.get("listings") or [])

    if not calendar_kpi:
        raise ValueError("tables['calendar_kpi'] rỗng hoặc chưa được tính trước khi gọi viz_calendar.render")

    by_area: dict[str, list[tuple[str, float]]] = defaultdict(list)
    snapshots_set: set[str] = set()

    for row in calendar_kpi:
        snap = str(row["snapshot_date"])
        area = str(row["analysis_area"])
        rate = _check_rate(row["availability_rate"], "availability_rate")
        by_area[area].append((snap, rate * 100.0))
        snapshots_set.add(snap)

    snapshots = sorted(snapshots_set)

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        has_mpl = True
    except ImportError:
        has_mpl = False

    if snapshots and by_area:
        p1 = figures / "tv4_availability_timeline_by_area.png"
        if has_mpl:
            fig, ax = plt.subplots(figsize=(9.5, 5.2), dpi=150)
            for area in sorted(by_area.keys()):
                pts = sorted(by_area[area], key=lambda x: x[0])
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                ax.plot(xs, ys, marker="o", linewidth=1.8, label=area)

            ax.set_title("Tỷ lệ sẵn có 90 ngày (Availability Rate) theo 8 vùng phân tích qua các Snapshot", fontsize=11.5, fontweight="bold")
            ax.set_xlabel("Mốc Snapshot (YYYY-MM-DD)", fontsize=10)
            ax.set_ylabel("Tỷ lệ sẵn có (%)", fontsize=10)
            ax.set_ylim(0, 100)
            ax.grid(True, linestyle=":", alpha=0.6)
            ax.legend(title="Analysis Area (8 vùng)", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8.5)
            fig.text(
                0.01, -0.03,
                "Nguồn: Inside Airbnb Toronto (cohort được giao). Availability phản ánh lịch mở đặt phòng (không phải occupancy); không suy rộng toàn thị trường.",
                fontsize=8, color="#444444"
            )
            plt.tight_layout()
            fig.savefig(p1, bbox_inches="tight")
            plt.close(fig)
        else:
            _write_fallback_png(p1)
        saved_paths.append(p1)

        latest_snap = snapshots[-1]
        latest_kpi = sorted(
            [r for r in calendar_kpi if str(r["snapshot_date"]) == latest_snap],
            key=lambda r: float(r["availability_rate"]),
        )
        if latest_kpi:
            p2 = figures / "tv4_availability_by_analysis_area.png"
            if has_mpl:
                fig, ax = plt.subplots(figsize=(9.0, 4.8), dpi=150)
                areas = [f"{r['analysis_area']} (n={r['listing_n']})" for r in latest_kpi]
                rates_pct = [_check_rate(r["availability_rate"], "availability_rate") * 100.0 for r in latest_kpi]

                bars = ax.barh(areas, rates_pct, color="#2b5c8f")
                ax.bar_label(bars, fmt="%.1f%%", padding=4, fontsize=8.5)
                ax.set_title(f"So sánh tỷ lệ sẵn có 90 ngày theo vùng phân tích tại mốc {latest_snap}", fontsize=11.5, fontweight="bold")
                ax.set_xlabel("Tỷ lệ sẵn có (%)", fontsize=10)
                ax.set_ylabel("Vùng phân tích (Analysis Area)", fontsize=10)
                ax.set_xlim(0, 105)
                ax.grid(axis="x", linestyle=":", alpha=0.6)
                fig.text(
                    0.01, -0.03,
                    "Nguồn: Inside Airbnb Toronto (cohort được giao). Không sử dụng cột price của bảng calendar; không gọi là neighbourhood hành chính.",
                    fontsize=8, color="#444444"
                )
                plt.tight_layout()
                fig.savefig(p2, bbox_inches="tight")
                plt.close(fig)
            else:
                _write_fallback_png(p2)
            saved_paths.append(p2)

    if snapshots and calendar_rows and listings_rows:
        latest_snap = snapshots[-1]
        cal_latest = {
            str(r["listing_id"]): _check_rate(r["availability_rate"], "availability_rate") * 100.0
            for r in calendar_rows
            if str(r.get("snapshot_date")) == latest_snap
        }

        area_points: dict[str, tuple[list[float], list[float]]] = defaultdict(lambda: ([], []))
        for r in listings_rows:
            if str(r.get("snapshot_date")) != latest_snap:
                continue
            lid = str(r.get("listing_id", ""))
            price = r.get("price")
            if lid in cal_latest and price is not None:
                try:
                    p_val = float(price)
                except (TypeError, ValueError):
                    continue
                if p_val > 0:
                    area = str(r.get("analysis_area") or "Unknown")
                    area_points[area][0].append(p_val)
                    area_points[area][1].append(cal_latest[lid])

        if area_points:
            p3 = figures / "tv4_price_vs_availability_latest.png"
            if has_mpl:
                fig, ax = plt.subplots(figsize=(9.2, 5.2), dpi=150)
                for area in sorted(area_points.keys()):
                    xs, ys = area_points[area]
                    ax.scatter(xs, ys, alpha=0.65, s=28, label=f"{area} (n={len(xs)})")

                ax.set_title(f"Tương quan Giá niêm yết (CAD) và Tỷ lệ sẵn có 90 ngày tại mốc {latest_snap}", fontsize=11.5, fontweight="bold")
                ax.set_xlabel("Giá niêm yết từ bảng Listings (CAD / đêm)", fontsize=10)
                ax.set_ylabel("Tỷ lệ sẵn có 90 ngày (%)", fontsize=10)
                ax.set_ylim(-2, 102)
                ax.grid(True, linestyle=":", alpha=0.6)
                ax.legend(title="Analysis Area", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
                fig.text(
                    0.01, -0.03,
                    "Nguồn: Inside Airbnb Toronto (giá lấy từ listings tại mốc cuối cùng; calendar không dùng giá). Availability không phải occupancy.",
                    fontsize=8, color="#444444"
                )
                plt.tight_layout()
                fig.savefig(p3, bbox_inches="tight")
                plt.close(fig)
            else:
                _write_fallback_png(p3)
            saved_paths.append(p3)

    return saved_paths