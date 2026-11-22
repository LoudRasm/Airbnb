"""TV3 — Nguyễn Quốc Hiếu: Giá mốc cuối, room type, host và maps theo analysis_area; không nhầm ranh giới hành chính."""


from pathlib import Path
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
from shapely.geometry import box
import plotly.express as px
import pandas as pd
from matplotlib import cm
from matplotlib.colors import Normalize
from .kpi import df_kpi, neighbourhood_summary

OWNER = 'TV3 — Nguyễn Quốc Hiếu'
IMPLEMENTED = True
READY = True  # Integration validated; see docs/VERIFICATION.md.

def _pyplot():
    import matplotlib.pyplot as plt
    return plt


def viz1_median_price(df_listings,df_kpi_summary, gdf_areas,cfg, path):
    plt = _pyplot()
    FINAL_SNAPSHOT = cfg.get('price_snapshot', cfg['snapshots'][-1])
    CURRENCY= cfg['currency']
    
    df_final = df_listings[df_listings['snapshot_date'] == FINAL_SNAPSHOT].copy()
    
    gdf_map1 = gdf_areas.merge(df_kpi_summary, on='analysis_area', how='left')

    # Phân vị 33% và 66% để xếp cấp độ
    q33 = gdf_map1['median_price'].quantile(0.33)
    q66 = gdf_map1['median_price'].quantile(0.66)

    vmin, vmax = gdf_map1['median_price'].min(), gdf_map1['median_price'].max()

    def get_tier(p):
        if pd.isna(p): return "N/A", "#e0e0e0"
        if p >= q66: return "Cao", "#ff7675"
        elif p >= q33: return "TB", "#ffeaa7"
        else: return "Thấp", "#55efc4"

    fig, ax = plt.subplots(figsize=(12, 8))

    # Vẽ 8 khung vùng
    if gdf_map1['median_price'].notna().any():
        gdf_map1.plot(column='median_price', cmap='YlOrRd', alpha=0.45,
                      edgecolor='black', linewidth=0.5, ax=ax, legend=False,
                      missing_kwds={'color': '#e0e0e0'})
        sm = cm.ScalarMappable(norm=Normalize(vmin=vmin, vmax=vmax), cmap='YlOrRd')
        cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', pad=0.10, fraction=0.04, shrink=0.8, alpha=0.45)
        cbar.set_label(f'Giá trung vị ({CURRENCY}/đêm)')
    else:
        gdf_map1.plot(color='#e0e0e0', edgecolor='black', linewidth=0.5, ax=ax)

    # Chồng các điểm listing thực tế
    valid_pts = df_final[df_final['latitude'].notna() & df_final['longitude'].notna()]
    ax.scatter(valid_pts['longitude'], valid_pts['latitude'], c='navy', s=8, alpha=0.4, label=f'Listings (n={len(valid_pts)})')

    # Thêm nhãn tên vùng, giá và độ lớn
    for _, row in gdf_map1.iterrows():
        c = row.geometry.centroid
        area = row['analysis_area']
        p = row['median_price']
        tier, box_color = get_tier(p)
        
        lbl = f"{area}\n{p:,.0f} {CURRENCY}\n[{tier}]" if pd.notna(p) else f"{area}\nN/A"
        ax.annotate(lbl, xy=(c.x, c.y), ha='center', va='center', fontsize=8, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', fc=box_color, ec='black', lw=1.1, alpha=0.5))

    ax.set_title(f"Phân bố Không gian & Mức giá 8 vùng Analysis Area ({FINAL_SNAPSHOT})", fontsize=13, fontweight='bold')
    ax.set_xlabel("Kinh độ")
    ax.set_ylabel("Vĩ độ")
    ax.legend(loc='upper right')

    plt.grid(True, linestyle=":", alpha=0.5)
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'Đã lưu fig1 ở {path}')
    return path





def viz2_choropleth(df_listings, toronto_geojson, cfg, path, neighbourhood_kpi=None):
    FINAL_SNAPSHOT = cfg.get('price_snapshot', cfg['snapshots'][-1])
    CURRENCY = cfg['currency']
    
    hood_stats = pd.DataFrame(
        neighbourhood_kpi if neighbourhood_kpi is not None 
        else neighbourhood_summary(df_listings, cfg)
    )
    if 'snapshot_date' in hood_stats.columns:
        hood_stats = hood_stats[hood_stats['snapshot_date'] == FINAL_SNAPSHOT].copy()

    valid_prices = hood_stats['median_price'].dropna()
    min_price = valid_prices.min() if not valid_prices.empty else 0
    max_price = valid_prices.quantile(0.95) if not valid_prices.empty else 500

    fig_choropleth = px.choropleth_mapbox(
        hood_stats,
        geojson=toronto_geojson,
        locations='neighbourhood_cleansed',
        featureidkey="properties.neighbourhood",
        color='median_price',
        color_continuous_scale="YlOrRd",
        range_color=(min_price, max_price),
        mapbox_style="white-bg",  # Đặt white-bg để tự định nghĩa layer OpenStreetMap bên dưới
        zoom=9.8,
        center={"lat": 43.70, "lon": -79.38},
        opacity=0.65,
        labels={
            'median_price': f'Giá trung vị ({CURRENCY})', 
            'supply': 'Số listing', 
            'neighbourhood_cleansed': 'Khu vực'
        },
        hover_data={'neighbourhood_cleansed': True, 'median_price': ':.0f', 'supply': True},
        title=f"<b>Bản đồ Choropleth Tương tác: Giá Trung vị theo Khu vực Hành chính ({FINAL_SNAPSHOT})</b>"
    )
    
    # Thêm lớp bản đồ OpenStreetMap qua server mirror của Pháp (OpenStreetMap France - không bị chặn 403)
    fig_choropleth.update_layout(
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                "source": [
                    "https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
                    # Hoặc server Đức: "https://tile.openstreetmap.de/{z}/{x}/{y}.png"
                ]
            }
        ],
        margin={"r": 0, "t": 40, "l": 0, "b": 0}, 
        height=600
    )
    
    path.parent.mkdir(parents=True, exist_ok=True)
    fig_choropleth.write_html(str(path))
    print(f'Đã lưu fig2 ở {path}')
    return path



def viz3_compare(df_kpi_summary, cfg, path):
    plt = _pyplot()
    FINAL_SNAPSHOT = cfg.get('price_snapshot', cfg['snapshots'][-1])
    fig, ax = plt.subplots(figsize=(10, 5))
    df_kpi_sorted = df_kpi_summary.sort_values("analysis_area")
    x = range(len(df_kpi_sorted))
    width = 0.35

    ax.bar(
        [i - width / 2 for i in x],
        df_kpi_sorted["entire_home_share"] * 100,
        width,
        label="Entire Home Share (%)",
    )
    ax.bar(
        [i + width / 2 for i in x],
        df_kpi_sorted["multi_listing_host_share"] * 100,
        width,
        label="Multi-host Share (%)",
    )

    # THÊM DÒNG NÀY: Tự động hiển thị số liệu chính xác trên đầu các cột
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=7.5)

    ax.set_xticks(list(x))
    ax.set_xticklabels(df_kpi_sorted["analysis_area"])
    ax.set_ylabel("Tỷ lệ (%)")
    ax.set_title(
        f"Cấu trúc Loại phòng & Mức độ Chuyên nghiệp của Host theo Vùng ({FINAL_SNAPSHOT})",
        fontsize=11,
    )

    # Mở rộng giới hạn trục Y một chút để số liệu ở cột cao nhất không bị che bởi khung
    ax.set_ylim(0, 110)

    ax.legend()
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    
    fig.savefig(path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f'Đã lưu fig3 ở {path}')
    return path
    
    


def render(tables, figures, cfg):
    """Đọc các bảng từ tables, lưu hình trong figures, trả list[Path].

    tables xem docs/CONTRACTS.md; figures là Path đã tạo; không sửa bảng đầu vào.
    """
    areas = cfg.get('analysis_areas')
    if not areas:
        raise ValueError('Spatial maps require cfg.analysis_areas rectangles from the assignment')
    FINAL_SNAPSHOT = cfg.get('price_snapshot', cfg['snapshots'][-1])
    figures = Path(figures)
    figures.mkdir(parents=True, exist_ok=True)

    boxes = [
        {"analysis_area": item["area"], "geometry": box(item["lon_min"], item["lat_min"], item["lon_max"], item["lat_max"])}
        for item in areas
    ]
    gdf_areas = gpd.GeoDataFrame(boxes, crs="EPSG:4326")   
    raw_listings = tables.get('listings', [])
    df_listings = pd.DataFrame(raw_listings) if isinstance(raw_listings, list) else raw_listings
    all_kpi = pd.DataFrame(tables['market_kpi']) if 'market_kpi' in tables else df_kpi(df_listings, cfg)
    list_path = []
    if FINAL_SNAPSHOT in set(df_listings['snapshot_date']):
        price_kpi = all_kpi[all_kpi['snapshot_date'] == FINAL_SNAPSHOT]
        toronto_geojson = tables['geojson'][FINAL_SNAPSHOT]
        list_path.append(viz1_median_price(df_listings, price_kpi, gdf_areas, cfg, figures/'viz1_median_price.png'))
        list_path.append(viz2_choropleth(df_listings, toronto_geojson, cfg, figures/'viz2_choropleth.html', tables.get('neighbourhood_kpi')))
    latest = cfg['snapshots'][-1]
    comparison_cfg = {**cfg, 'price_snapshot': latest}
    latest_kpi = all_kpi[all_kpi['snapshot_date'] == latest]
    list_path.append(viz3_compare(latest_kpi, comparison_cfg, figures/'viz3_compare.png'))
    return list_path
