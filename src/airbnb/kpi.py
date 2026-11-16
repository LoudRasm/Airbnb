"""TV3 — Nguyễn Quốc Hiếu. Khung công việc cả kỳ; chưa triển khai.

Không import hoặc chạy pipeline ở cấp module. Giữ chữ ký hàm để TV1 tích hợp.
"""

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import json
import pandas as pd
import geopandas as gpd
from src.airbnb.io import load_config
import matplotlib.pyplot as plt
from shapely.geometry import box
import plotly.express as px



OWNER = 'TV3 — Nguyễn Quốc Hiếu'
READY = False  # Chỉ bật True sau khi triển khai, có test và review.




def df_kpi(df_listings,cfg):
    final_snapshot = cfg['snapshots'][-1]
    print("Mốc thời gian cuối cùng (để tính giá):", final_snapshot)



    # 1. Đọc dữ liệu listings

    df_final = df_listings[df_listings['snapshot_date'] == final_snapshot].copy()
    print(f"Đã nạp {len(df_final)} listing mốc cuối ({final_snapshot})")

    
    
    df_final = df_listings[df_listings['snapshot_date'] == final_snapshot].copy()
    # 1. Supply & Median Price
    price_stats = df_final.groupby('analysis_area').agg(
        supply=('listing_id', 'count'),
        median_price=('price', 'median'),
        price_n=('price', 'count')
    ).reset_index()

    # 2. Entire Home Share (Mẫu số = các dòng có room_type hợp lệ)
    valid_room = df_final[df_final['room_type'].notna() & (df_final['room_type'] != '')]
    room_stats = valid_room.groupby('analysis_area').apply(
        lambda g: (g['room_type'] == 'Entire home/apt').mean(),
        include_groups=False
    ).reset_index(name='entire_home_share')

    # 3. Multi-listing Host Share (Host có > 1 listing trong mốc)
    valid_host = df_final[df_final['host_id'].notna() & (df_final['host_id'] != '')].copy()
    host_counts = valid_host.groupby('host_id')['listing_id'].transform('count')
    valid_host['is_multi_host'] = host_counts > 1
    host_stats = valid_host.groupby('analysis_area')['is_multi_host'].mean().reset_index(name='multi_listing_host_share')

    # Gom hợp thành 1 bảng tổng hợp KPI
    df_kpi_summary = price_stats.merge(room_stats, on='analysis_area', how='left')
    df_kpi_summary = df_kpi_summary.merge(host_stats, on='analysis_area', how='left')
    
    if "currency" not in df_kpi_summary.columns:
        df_kpi_summary["currency"] = cfg.get("currency", "CAD")

    if "snapshot_date" not in df_kpi_summary.columns:
        df_kpi_summary["snapshot_date"] = final_snapshot
        
    return df_kpi_summary    


def summarize(listings, cfg):
    """Trả list[dict]: snapshot_date, analysis_area, supply, median_price, price_n,
    currency, entire_home_share, multi_listing_host_share. Giá ngoài mốc cuối để trống.
    """
    # TODO[TV3]: Tính giá chỉ mốc cuối, room type và host; ghi rõ công thức/denominator.
    # TODO[TV3]: Nhận analysis_area từ workbook; phân biệt vùng phân tích với neighbourhood.
    # TODO[TV3]: Không tự tính availability/guest KPI ở đây; Nam/Phan Huy sở hữu phần đó.
    # TODO[TV3]: Các KPI phản ánh 1.000 ID được giao, không suy rộng toàn Toronto.
    cfg, root_path = load_config(ROOT/ "configs/toronto.yaml")
    df_listings = pd.read_csv(ROOT / 'data/processed/real/listings.csv')
    
    df_kpi_summary = df_kpi(df_listings, cfg)

    return df_kpi_summary.to_dict(orient="records")
    


#Demo
df_listings_demo = pd.read_csv(ROOT / 'data/processed/real/listings.csv')
cfg, _ =load_config(ROOT/ "configs/toronto.yaml")

if __name__ == '__main__':
    print(summarize(df_listings_demo,cfg))