# Tự triển khai module và nối vào pipeline

Phần data check đang dùng giữ nguyên. Phần phân tích cả kỳ là khung để thành viên viết code,
không phải các thuật toán đã hoàn thành. Có thể tìm task bằng `rg 'TODO\[TV' src/airbnb`.
Các implementation từ bản starter trước nằm trong lịch sử Git, không được trình bày là code
các bạn tự viết. AI_USAGE ghi rõ khung/implementation do AI tạo.

## Thành viên làm gì

Ví dụ Đức:

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/duc-qa
# Triển khai clean_listings trong src/airbnb/qa.py; giữ chữ ký và contract
# Thêm tests/test_qa.py, docs/QA.md và report section
python -m unittest discover -s tests -v
python run_pipeline.py --status
git add src/airbnb/qa.py tests/test_qa.py docs/QA.md AI_USAGE.md
git commit -m "feat(qa): implement and validate assigned-data rules"
git push -u origin feat/duc-qa
```

Mở PR vào main. READY là trạng thái kỹ thuật của module, không tự chứng minh chất lượng;
chỉ bật True sau khi các hàm của module đã xong/test/review. Không trả dữ liệu giả hoặc list rỗng
để vượt TODO. CI nền chạy được khi vẫn còn TODO; test của thuật toán do chính owner bổ sung.
Module chưa xong phải tiếp tục báo NotImplementedError khi gọi.

Mỗi file có OWNER, chữ ký hàm, mô tả input/output và TODO của người phụ trách.
Không đổi toàn bộ pipeline, không sửa data_check để làm bài phân tích.
Nếu thêm dependency, ghim phiên bản và chạy lại môi trường sạch.

## Nhóm trưởng nối code thế nào

Code hiện đã import các module:

```python
from airbnb import qa, calendar, reviews, kpi

cleaned, report = qa.clean_listings(raw_listings, snapshot, cfg)
calendar_rows, issues = calendar.aggregate(raw_calendar, snapshot, window_days, listing_ids)
review_issues = reviews.collect(raw_reviews, snapshot, review_map)
market_kpi = kpi.summarize(all_cleaned_listings, cfg)
```

Đây là lời gọi, **không phải triển khai thuật toán**. Sau khi PR của Đức/Nam/Phan Huy/Hiếu merge
vào đúng file và đúng chữ ký, import tự dùng implementation mới. Không cần chép code của các bạn
vào run_pipeline.py. Nhóm trưởng quản lý thứ tự bước và xuất file; owner viết logic và tests.

Nếu một bạn tạo file mới, ví dụ `src/airbnb/calendar_extra.py`:

```python
# Trong file thành viên: chỉ định nghĩa hàm, không đọc raw/gọi API ngay khi import.
def build_temporal_kpi(calendar_rows, cfg):
    # TODO[TV4]: triển khai và trả list[dict] theo contract đã thống nhất
    raise NotImplementedError

# Trong pipeline sau khi PR được review/merge:
from airbnb.calendar_extra import build_temporal_kpi
# tables['calendar_kpi'] = build_temporal_kpi(calendars, cfg)
```

Đổi tên/chữ ký/output qua issue và cập nhật CONTRACTS trước merge.
Không import script có top-level code tải file/chạy API; phần chạy riêng cần nằm dưới
`if __name__ == '__main__':`. Không dùng output in terminal làm interface giữa các module.
Hàm trả bảng dữ liệu/diagnostics hoặc paths; pipeline chung mới ghi CSV/metadata.

## Vẽ và KPI không đụng file người khác

Hiếu sở hữu kpi.py và viz_spatial.py. Nam sở hữu calendar.metrics và viz_calendar.py.
Phan Huy sở hữu review_kpi.py và viz_reviews.py. Đức sở hữu viz_qa.py.
Nhóm trưởng sở hữu analysis.py và viz_market.py; viz.py chỉ gọi render của các file này.

## Đầu vào và giới hạn bắt buộc

Loader của TV1 đọc config/workbook, lọc listing/calendar theo 1.000 listing ID và reviews theo
5.000 review ID độc lập listing_id, thêm analysis_area từ workbook cho listings.
QA nhận iterator, không tự tải dữ liệu. Calendar phải xử lý streaming.
Giá chỉ dùng mốc cuối; không dùng giá calendar. 1.000 ID cố định không đo được market entry/exit
của toàn thành phố; TV1 cần giải thích/điều chỉnh metric market evolution.
LLM dùng đúng 1.000 ID được giao. 100 dòng đánh dấu x là IDs cần gán nhãn, chưa là nhãn sentiment.

## Kiểm tra trạng thái

```bash
python run_pipeline.py --status
python run_pipeline.py --status --skip-llm
```

Chạy pipeline phân tích thật hoặc demo khi còn module bắt buộc READY=False sẽ dừng trước
network/output. Khi mọi module đã triển khai, lệnh cũ vẫn là:

```bash
python run_pipeline.py --config configs/toronto.yaml --skip-llm
python run_pipeline.py --config configs/toronto.yaml
```

Lệnh đầy đủ cần workbook, raw, GEMINI_API_KEY và nhãn sentiment thật của 100 review được giao.
`--skip-llm` bỏ API/evaluation/guest KPI/hình reviews; không phải lệnh nộp cuối đủ phần LLM.
Data check vẫn chạy độc lập bằng scripts/check_data.py và không phụ thuộc các READY/TODO này.
