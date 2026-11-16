"""
Unit tests kiểm thử các trường hợp biên (edge cases) cho module KPI (kpi.py).
Bao gồm: missing/invalid price, 0 mẫu hợp lệ, host trống, nhóm rỗng,
nhiều mốc snapshot, mẫu số (denominator) và vùng không join được.

Tác giả: Nguyễn Quốc Hiếu (TV3)
"""

import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

# Thêm thư mục gốc vào sys.path để import module src
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.airbnb.kpi import df_kpi, summarize


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_cfg():
    """Config giả lập với 2 mốc thời gian để test lọc mốc cuối."""
    return {"snapshots": ["2023-09-01", "2023-12-01"], "currency": "CAD"}


# ---------------------------------------------------------------------------
# 1. TEST MISSING / INVALID PRICE
# ---------------------------------------------------------------------------
def test_missing_and_invalid_price(mock_cfg):
    """Kiểm tra xử lý khi giá bị thiếu (NaN) hoặc không hợp lệ."""
    df_listings = pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4],
            "snapshot_date": ["2023-12-01"] * 4,
            "analysis_area": ["A01"] * 4,
            "price": [100.0, np.nan, 200.0, None],  # 2 mẫu hợp lệ, 2 mẫu NaN/None
            "room_type": ["Entire home/apt"] * 4,
            "host_id": [101, 102, 103, 104],
        }
    )

    df_res = df_kpi(df_listings, mock_cfg)
    row_a01 = df_res[df_res["analysis_area"] == "A01"].iloc[0]

    # Kiểm tra: supply = 4, nhưng price_n chỉ đếm 2 mẫu hợp lệ, median_price = 150.0
    assert row_a01["supply"] == 4
    assert row_a01["price_n"] == 2
    assert row_a01["median_price"] == 150.0


# ---------------------------------------------------------------------------
# 2. TEST 0 MẪU HỢP LỆ (ALL PRICES ARE NaN)
# ---------------------------------------------------------------------------
def test_zero_valid_samples(mock_cfg):
    """Kiểm tra vùng có 0 mẫu giá hợp lệ (toàn bộ NaN), không làm sập chương trình."""
    df_listings = pd.DataFrame(
        {
            "listing_id": [1, 2],
            "snapshot_date": ["2023-12-01"] * 2,
            "analysis_area": ["A01"] * 2,
            "price": [np.nan, None],  # 0 mẫu giá hợp lệ
            "room_type": ["Private room"] * 2,
            "host_id": [101, 102],
        }
    )

    df_res = df_kpi(df_listings, mock_cfg)
    row_a01 = df_res[df_res["analysis_area"] == "A01"].iloc[0]

    assert row_a01["supply"] == 2
    assert row_a01["price_n"] == 0
    assert pd.isna(row_a01["median_price"])


# ---------------------------------------------------------------------------
# 3. TEST HOST TRỐNG (NaN HOẶC CHUỖI RỖNG)
# ---------------------------------------------------------------------------
def test_empty_and_invalid_host(mock_cfg):
    """Kiểm tra xử lý host_id bị trống (NaN, rỗng '') không làm sai lệch multi-host share."""
    df_listings = pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4],
            "snapshot_date": ["2023-12-01"] * 4,
            "analysis_area": ["A01"] * 4,
            "price": [100.0] * 4,
            "room_type": ["Entire home/apt"] * 4,
            "host_id": [1001, 1001, np.nan, ""],  # Host 1001 xuất hiện 2 lần (multi-host), 2 dòng trống
        }
    )

    df_res = df_kpi(df_listings, mock_cfg)
    row_a01 = df_res[df_res["analysis_area"] == "A01"].iloc[0]

    # Chỉ có 2 dòng của host 1001 là hợp lệ và cả 2 đều thuộc multi-host => 100% (1.0)
    assert row_a01["multi_listing_host_share"] == 1.0


# ---------------------------------------------------------------------------
# 4. TEST NHÓM RỖNG / DATAFRAME RỖNG
# ---------------------------------------------------------------------------
def test_empty_dataframe_and_groups(mock_cfg):
    """Kiểm tra truyền vào DataFrame rỗng hoặc không có dữ liệu mốc cuối."""
    df_empty = pd.DataFrame(
        columns=[
            "listing_id",
            "snapshot_date",
            "analysis_area",
            "price",
            "room_type",
            "host_id",
        ]
    )

    df_res = df_kpi(df_empty, mock_cfg)
    assert df_res.empty


# ---------------------------------------------------------------------------
# 5. TEST NHIỀU MỐC THỜI GIAN (MULTIPLE SNAPSHOTS)
# ---------------------------------------------------------------------------
def test_multiple_snapshots_filtering(mock_cfg):
    """Kiểm tra chỉ lọc dữ liệu của mốc cuối cùng ('2023-12-01') theo cfg['snapshots'][-1]."""
    df_listings = pd.DataFrame(
        {
            "listing_id": [101, 102, 201],
            "snapshot_date": ["2023-09-01", "2023-09-01", "2023-12-01"],
            "analysis_area": ["A01", "A01", "A01"],
            "price": [50.0, 60.0, 300.0],  # 201 mốc mới có giá 300.0
            "room_type": ["Entire home/apt"] * 3,
            "host_id": [1, 2, 3],
        }
    )

    df_res = df_kpi(df_listings, mock_cfg)
    row_a01 = df_res[df_res["analysis_area"] == "A01"].iloc[0]

    # Chỉ có 1 listing ở mốc cuối '2023-12-01'
    assert row_a01["supply"] == 1
    assert row_a01["median_price"] == 300.0
    assert row_a01["snapshot_date"] == "2023-12-01"


# ---------------------------------------------------------------------------
# 6. TEST MẪU SỐ (DENOMINATOR) TÍNH TỶ LỆ ROOM TYPE & HOST
# ---------------------------------------------------------------------------
def test_denominator_accuracy(mock_cfg):
    """Kiểm tra mẫu số (denominator) khi tính entire_home_share khi có dòng room_type bị NaN."""
    df_listings = pd.DataFrame(
        {
            "listing_id": [1, 2, 3, 4],
            "snapshot_date": ["2023-12-01"] * 4,
            "analysis_area": ["A01"] * 4,
            "price": [100.0] * 4,
            "room_type": [
                "Entire home/apt",
                "Private room",
                np.nan,
                "",
            ],  # 2 dòng hợp lệ (1 Entire, 1 Private)
            "host_id": [101, 102, 103, 104],
        }
    )

    df_res = df_kpi(df_listings, mock_cfg)
    row_a01 = df_res[df_res["analysis_area"] == "A01"].iloc[0]

    # Denominator cho room_type hợp lệ là 2 dòng => 1 / 2 = 0.5 (50%)
    assert row_a01["entire_home_share"] == 0.5


# ---------------------------------------------------------------------------
# 7. TEST VÙNG KHÔNG JOIN ĐƯỢC (MISSING / UNJOINED AREA)
# ---------------------------------------------------------------------------
def test_unjoined_and_missing_analysis_area(mock_cfg):
    """Kiểm tra khi chứa mã vùng lạ (vd 'A99') không nằm trong các vùng chuẩn."""
    df_listings = pd.DataFrame(
        {
            "listing_id": [1, 2],
            "snapshot_date": ["2023-12-01"] * 2,
            "analysis_area": ["A01", "A99"],  # A99 là vùng lạ
            "price": [100.0, 200.0],
            "room_type": ["Entire home/apt"] * 2,
            "host_id": [101, 102],
        }
    )

    df_res = df_kpi(df_listings, mock_cfg)

    # Đảm bảo phân nhóm giữ lại đầy đủ cả vùng lạ A99 mà không văng lỗi
    assert set(df_res["analysis_area"]) == {"A01", "A99"}
    assert len(df_res) == 2


# ---------------------------------------------------------------------------
# 8. TEST CONTRACT TRẢ VỀ CỦA HÀM SUMMARIZE
# ---------------------------------------------------------------------------
def test_summarize_contract_with_edge_cases(mock_cfg):
    """Kiểm tra hàm summarize trả về list[dict] chuẩn contract dù dữ liệu dính lỗi edge cases."""
    df_listings = pd.DataFrame(
        {
            "listing_id": [1, 2],
            "snapshot_date": ["2023-12-01"] * 2,
            "analysis_area": ["A01", "A02"],
            "price": [np.nan, 150.0],
            "room_type": [None, "Entire home/apt"],
            "host_id": ["", 102],
        }
    )

    with (
        patch("src.airbnb.kpi.load_config", return_value=(mock_cfg, Path("."))),
        patch("pandas.read_csv", return_value=df_listings),
    ):
        res = summarize(df_listings, mock_cfg)

        assert isinstance(res, list)
        assert len(res) == 2
        for item in res:
            assert isinstance(item, dict)
            assert "analysis_area" in item
            assert "median_price" in item
            assert "entire_home_share" in item
            assert "multi_listing_host_share" in item