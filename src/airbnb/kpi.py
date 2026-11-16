"""TV3 — Nguyễn Quốc Hiếu. KPI theo mốc và vùng.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

import pandas as pd

OWNER = 'TV3 — Nguyễn Quốc Hiếu'
IMPLEMENTED = True
READY = True  # Integration validated; see docs/VERIFICATION.md.



def _snapshot_kpi(df_listings, cfg: dict) -> pd.DataFrame:
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
    if isinstance(df_listings, list):
        df_listings = pd.DataFrame(df_listings)
    if df_listings is None or df_listings.empty:
        return pd.DataFrame(columns=expected_cols)

    final_snapshot = cfg.get("snapshots", [None])[-1]
    currency = cfg.get("currency", "CAD")

    df_final = df_listings.copy()
    final_snapshot = str(df_final['snapshot_date'].iloc[0])
    price_snapshot = cfg.get('price_snapshot', cfg['snapshots'][-1])
    if final_snapshot != price_snapshot:
        df_final['price'] = float('nan')
    df_final['price'] = pd.to_numeric(df_final['price'], errors='coerce')

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

    # Bổ sung cột currency và snapshot_date
    df_kpi_summary["currency"] = currency
    df_kpi_summary["snapshot_date"] = final_snapshot

    return df_kpi_summary


def df_kpi(df_listings, cfg):
    """Supply/room/host by date and area; price only at configured price_snapshot."""
    frame = pd.DataFrame(df_listings) if isinstance(df_listings, list) else df_listings
    if frame is None or frame.empty:
        return _snapshot_kpi([], cfg)
    return pd.concat([_snapshot_kpi(part, cfg) for _, part in frame.groupby('snapshot_date', sort=True)], ignore_index=True)


def summarize(listings, cfg):
    frame = df_kpi(listings, cfg)
    return frame.astype(object).where(frame.notna(), None).to_dict(orient='records')


def neighbourhood_summary(listings, cfg):
    """Same formulas, grouped by official neighbourhood; all listings count toward supply."""
    frame = pd.DataFrame(listings)
    if frame.empty:
        return []
    frame['analysis_area'] = frame['neighbourhood_cleansed'].fillna('').replace('', 'Unknown')
    return [{('neighbourhood_cleansed' if key == 'analysis_area' else key): value
             for key, value in row.items()} for row in summarize(frame, cfg)]
