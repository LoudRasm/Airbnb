"""TV2 — Mai Anh Đức: thống kê cờ QA sau cleaning (EDA tối thiểu theo contract).

Không import hoặc chạy pipeline ở cấp module.
"""
from collections import Counter

OWNER = 'TV2 — Mai Anh Đức'
READY = True 


def profile(listings):
    """Đếm số listing theo từng cờ QA ở mỗi mốc: [{snapshot_date, qa_flags, count}].

    Mỗi dòng nhiều cờ được đếm vào từng cờ (cột qa_flags ở đây là MỘT tên cờ, không phải chuỗi
    nối '|'); dòng không có cờ được đếm vào 'none'. Không sửa bảng cleaned. Sắp xếp theo mốc
    rồi tên cờ để kết quả ổn định.
    """
    counts = Counter()
    for row in listings:
        for flag in (row['qa_flags'].split('|') if row['qa_flags'] else ['none']):
            counts[(row['snapshot_date'], flag)] += 1
    return [{'snapshot_date': snapshot, 'qa_flags': flag, 'count': n}
            for (snapshot, flag), n in sorted(counts.items())]
