"""TV3 — Nguyễn Quốc Hiếu. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import pandas as pd
from src.airbnb.io import load_config




OWNER = 'TV3 — Nguyễn Quốc Hiếu'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.

df_listings_demo = pd.read_csv(ROOT / 'data/processed/real/listings.csv')
cfg, _ =load_config(ROOT/ "configs/toronto.yaml")


def df_kpi(df_listings: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Tính toán các chỉ số KPI theo từng vùng analysis_area từ DataFrame listings."""
    # 0. Kiểm tra nếu DataFrame đầu vào rỗng
    expected_cols = [
        "analysis_area",
        "supply",
        "median_price",
        "price_n",
        "entire_home_share",
        "multi_listing_host_share",
        "currency",
        "snapshot_date",
    ]
    if df_listings is None or df_listings.empty:
        return pd.DataFrame(columns=expected_cols)

    final_snapshot = cfg.get("snapshots", [None])[-1]
    currency = cfg.get("currency", "CAD")

    # Lọc dữ liệu mốc thời gian cuối cùng
    if "snapshot_date" in df_listings.columns and final_snapshot is not None:
        df_final = df_listings[
            df_listings["snapshot_date"] == final_snapshot
        ].copy()
    else:
        df_final = df_listings.copy()

    if df_final.empty:
        return pd.DataFrame(columns=expected_cols)

    # 1. Supply & Median Price
    price_stats = (
        df_final.groupby("analysis_area")
        .agg(
            supply=("listing_id", "count"),
            median_price=("price", "median"),
            price_n=("price", "count"),
        )
        .reset_index()
    )

    # 2. Entire Home Share (Tránh dùng apply, dùng phép gán trực tiếp lên Series)
    valid_room = df_final[
        df_final["room_type"].notna() & (df_final["room_type"] != "")
    ].copy()

    if not valid_room.empty:
        valid_room["is_entire"] = (
            valid_room["room_type"] == "Entire home/apt"
        ).astype(float)
        room_stats = (
            valid_room.groupby("analysis_area")["is_entire"]
            .mean()
            .reset_index(name="entire_home_share")
        )
    else:
        room_stats = pd.DataFrame(
            columns=["analysis_area", "entire_home_share"]
        )

    # 3. Multi-listing Host Share
    valid_host = df_final[
        df_final["host_id"].notna() & (df_final["host_id"] != "")
    ].copy()

    if not valid_host.empty:
        host_counts = valid_host.groupby("host_id")["listing_id"].transform(
            "count"
        )
        valid_host["is_multi_host"] = (host_counts > 1).astype(float)
        host_stats = (
            valid_host.groupby("analysis_area")["is_multi_host"]
            .mean()
            .reset_index(name="multi_listing_host_share")
        )
    else:
        host_stats = pd.DataFrame(
            columns=["analysis_area", "multi_listing_host_share"]
        )

    # Gom các bảng thành 1 bảng tổng hợp KPI
    df_kpi_summary = price_stats.merge(
        room_stats, on="analysis_area", how="left"
    )
    df_kpi_summary = df_kpi_summary.merge(
        host_stats, on="analysis_area", how="left"
    )

    # Điền giá trị 0.0 cho các tỷ lệ nếu bị NaN do thiếu dữ liệu
    df_kpi_summary["entire_home_share"] = df_kpi_summary[
        "entire_home_share"
    ].fillna(0.0)
    df_kpi_summary["multi_listing_host_share"] = df_kpi_summary[
        "multi_listing_host_share"
    ].fillna(0.0)

    # Bổ sung cột currency và snapshot_date
    df_kpi_summary["currency"] = currency
    df_kpi_summary["snapshot_date"] = final_snapshot

    return df_kpi_summary


def summarize(listings: pd.DataFrame, cfg: dict):
    """Trả list[dict]: snapshot_date, analysis_area, supply, median_price, price_n,

    currency, entire_home_share, multi_listing_host_share.
    """
    df_kpi_summary = df_kpi(listings, cfg)
    return df_kpi_summary.to_dict(orient="records")


if __name__ == '__main__':
    print(summarize(df_listings_demo,cfg))