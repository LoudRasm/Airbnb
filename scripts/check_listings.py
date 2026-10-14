"""TV2 - QA: kiểm tra listings của nhóm ở 4 mốc, ghi kết quả ra CSV.

Cách dùng (chạy từ bất kỳ thư mục nào):
    python qa_tv2.py

Sửa 3 hằng số CẤU HÌNH bên dưới cho đúng máy của bạn.
Cần: pip install pandas openpyxl
"""
from pathlib import Path
import os
import pandas as pd

# ===================== CẤU HÌNH =====================
RAW_DIR = Path(r"C:\Users\ADMIN\Desktop\LTXLDL\Airbnb\raw")   # chứa các thư mục 2025-09-11, ...
WORKBOOK = Path(r"C:\Users\ADMIN\Downloads\Phân công thành phố cho project cuối kỳ.xlsx")
LOP, NHOM = "UET.DSE2049 1", "10"
OUT_DIR = Path(__file__).resolve().parent                      # nơi ghi file kết quả
# ====================================================

NGAY = ["2025-09-11", "2025-12-12", "2026-03-19", "2026-06-15"] 
NGUONG_NAN = 0.9


def lay_ma_va_id():
    """Lấy mã dữ liệu và tập listing_id của nhóm từ sheet 'Listing'."""
    df = pd.read_excel(WORKBOOK, sheet_name="Listing", dtype=str)
    g = df[(df["Lớp"] == LOP) & (df["Nhóm"].astype(float) == float(NHOM))]
    ma = g["Mã dữ liệu"].iloc[0]
    ids = set(g["listing_id"].str.strip())
    return ma, ids


def kiem_tra_mot_moc(moc, ngay, ids):
    path = RAW_DIR / ngay / "listings.csv.gz"
    df = pd.read_csv(path, low_memory=False)       # pandas tự giải nén .gz
    df["id"] = df["id"].astype(str).str.strip()
    s = df[df["id"].isin(ids)]                     # lọc theo ID của nhóm

    ty_le_thieu = s.isna().mean()                  # ô rỗng tính là NaN
    cot_nan_90 = ty_le_thieu[ty_le_thieu >= NGUONG_NAN].index.tolist()

    return {
        "moc": moc,
        "ngay": ngay,
        "listings_bytes": os.path.getsize(path),   # dung lượng file .gz
        "listings_dong": len(s),
        "so_cot_listings": s.shape[1],
        "so_cot_nan_90": len(cot_nan_90),
        "cot_nan_90": "; ".join(cot_nan_90),
        "id_khong_tim_thay": len(ids - set(s["id"])),
    }, ty_le_thieu


def main():
    ma, ids = lay_ma_va_id()
    print(f"Mã dữ liệu: {ma} | số ID của nhóm: {len(ids)}")

    ket_qua, bang_thieu = [], {}
    for moc, ngay in enumerate(NGAY, start=1):
        dong, ty_le = kiem_tra_mot_moc(moc, ngay, ids)
        dong = {"ma_du_lieu": ma, **dong}
        ket_qua.append(dong)
        bang_thieu[ngay] = ty_le
        print(f"Mốc {moc} ({ngay}): {dong['listings_dong']} dòng, "
              f"{dong['so_cot_listings']} cột, {dong['so_cot_nan_90']} cột NaN>=90%")

    # 1) Bảng tóm tắt TV2 (4 dòng, mỗi dòng một mốc)
    out1 = OUT_DIR / f"check_listings.csv"
    pd.DataFrame(ket_qua).to_csv(out1, index=False, encoding="utf-8")

    # 2) Tỷ lệ thiếu của từng cột ở từng mốc (phục vụ qa_report / Câu 3)
    out2 = OUT_DIR / f"ty_le_thieu_listings.csv"
    pd.DataFrame(bang_thieu).round(4).rename_axis("cot").to_csv(out2, encoding="utf-8")

    print("Đã ghi:", out1)
    print("Đã ghi:", out2)


if __name__ == "__main__":
    main()
