"""
Unit tests cho module KPI và Viz Spatial (Dự án Airbnb Toronto).
Tác giả: Nguyễn Quốc Hiếu (TV3)
"""

import json
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import pytest


from src.airbnb.kpi import df_kpi, summarize
from src.airbnb.viz_spatial import render


# ---------------------------------------------------------------------------
# FIXTURES (Dữ liệu giả lập cho Test)
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_cfg():
    """Tạo mock config yaml cho Toronto."""
    return {"snapshots": ["2023-12-01"], "currency": "CAD"}


@pytest.fixture
def mock_listings_df():
    """Tạo DataFrame listings mẫu để test tính toán KPI và vẽ biểu đồ."""
    return pd.DataFrame(
        {
            "listing_id": [101, 102, 103, 104, 105],
            "snapshot_date": [
                "2023-12-01",
                "2023-12-01",
                "2023-12-01",
                "2023-12-01",
                "2023-12-01",
            ],
            "analysis_area": ["A01", "A01", "A02", "A02", "A03"],
            "price": [150.0, 200.0, 300.0, 120.0, 90.0],
            "room_type": [
                "Entire home/apt",
                "Private room",
                "Entire home/apt",
                "Private room",
                "Entire home/apt",
            ],
            "host_id": [1001, 1001, 1002, 1003, 1004],  # Host 1001 sở hữu 2 listing -> multi host
            "latitude": [43.65, 43.66, 43.67, 43.68, 43.69],
            "longitude": [-79.38, -79.39, -79.40, -79.41, -79.42],
            "neighbourhood_cleansed": [
                "Kensington-Chinatown",
                "Kensington-Chinatown",
                "Waterfront Communities",
                "Waterfront Communities",
                "Annex",
            ],
        }
    )


@pytest.fixture
def mock_geojson_dict():
    """Tạo cấu trúc GeoJSON tối giản đại diện cho các khu vực ở Toronto."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"neighbourhood": "Kensington-Chinatown"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-79.40, 43.64],
                            [-79.38, 43.64],
                            [-79.38, 43.66],
                            [-79.40, 43.66],
                            [-79.40, 43.64],
                        ]
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {"neighbourhood": "Waterfront Communities"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-79.42, 43.66],
                            [-79.39, 43.66],
                            [-79.39, 43.68],
                            [-79.42, 43.68],
                            [-79.42, 43.66],
                        ]
                    ],
                },
            },
            {
                "type": "Feature",
                "properties": {"neighbourhood": "Annex"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-79.43, 43.68],
                            [-79.41, 43.68],
                            [-79.41, 43.70],
                            [-79.43, 43.70],
                            [-79.43, 43.68],
                        ]
                    ],
                },
            },
        ],
    }


# ---------------------------------------------------------------------------
# TESTS CHO MODULE KPI (kpi.py)
# ---------------------------------------------------------------------------
def test_df_kpi_calculation(mock_listings_df, mock_cfg):
    """Kiểm tra logic tính toán KPI trong hàm df_kpi."""
    df_result = df_kpi(mock_listings_df, mock_cfg)

    # 1. Kiểm tra các cột đầu ra đúng yêu cầu contract
    expected_cols = {
        "analysis_area",
        "supply",
        "median_price",
        "price_n",
        "entire_home_share",
        "multi_listing_host_share",
        "currency",
        "snapshot_date",
    }
    assert expected_cols.issubset(set(df_result.columns))

    # 2. Kiểm tra số lượng vùng analysis_area
    assert len(df_result) == 3

    # 3. Kiểm tra tính toán vùng A01 (2 listings: 150 & 200 => median=175.0, 1 entire home => 50% entire share, host 1001 là multi-host)
    row_a01 = df_result[df_result["analysis_area"] == "A01"].iloc[0]
    assert row_a01["supply"] == 2
    assert row_a01["median_price"] == 175.0
    assert row_a01["entire_home_share"] == 0.5
    assert row_a01["multi_listing_host_share"] == 1.0


def test_summarize_return_contract(mock_listings_df, mock_cfg):
    """Kiểm tra hàm summarize trả về list[dict] đúng định dạng hợp đồng."""
    # Patch load_config và read_csv để hàm summarize dùng mock data khi test
    with (
        patch("src.airbnb.kpi.load_config", return_value=(mock_cfg, Path("."))),
        patch("pandas.read_csv", return_value=mock_listings_df),
    ):
        result = summarize(mock_listings_df, mock_cfg)

        # Kiểm tra kĩ kiểu dữ liệu đầu ra phải là list[dict]
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], dict)

        # Kiểm tra thuộc tính bắt buộc trong mỗi dictionary
        first_item = result[0]
        assert "analysis_area" in first_item
        assert "median_price" in first_item
        assert "entire_home_share" in first_item
        assert "multi_listing_host_share" in first_item


# ---------------------------------------------------------------------------
# TESTS CHO MODULE VIZ SPATIAL (viz_spatial.py)
# ---------------------------------------------------------------------------
import json
from unittest.mock import mock_open, patch

# Lưu lại hàm open gốc của Python
_real_open = open


def custom_open(file, *args, **kwargs):
    """Chỉ mock khi mở file neighbourhoods.geojson, các file khác (như của Plotly) giữ nguyên."""
    if "neighbourhoods.geojson" in str(file):
        # Giả lập nội dung file GeoJSON bằng chuỗi JSON từ mock_geojson_dict
        return mock_open(read_data=json.dumps(mock_geojson_dict_data))()
    return _real_open(file, *args, **kwargs)


def test_render_output_files(
    mock_listings_df, mock_cfg, mock_geojson_dict, tmp_path
):
    """Kiểm tra hàm render xuất đúng 3 file hình ảnh/html vào thư mục figures."""
    # Lưu mock_geojson_dict vào biến toàn cục tạm thời để custom_open sử dụng
    global mock_geojson_dict_data
    mock_geojson_dict_data = mock_geojson_dict

    tables = {"listings": mock_listings_df}
    figures_dir = tmp_path / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    # Bỏ patch("json.load") toàn cục, chỉ chặn open có điều kiện và Path.exists
    with (
        patch("builtins.open", side_effect=custom_open),
        patch("pathlib.Path.exists", return_value=True),
    ):
        paths = render(tables, figures_dir, mock_cfg)

    # 1. Kiểm tra danh sách đường dẫn trả về gồm 3 file
    assert isinstance(paths, list)
    assert len(paths) == 3

    # 2. Kiểm tra sự tồn tại của 3 file trên đĩa
    for p in paths:
        assert Path(p).exists()

    # 3. Kiểm tra đúng định dạng đuôi file xuất ra (.png và .html)
    extensions = [Path(p).suffix for p in paths]
    assert ".png" in extensions
    assert ".html" in extensions