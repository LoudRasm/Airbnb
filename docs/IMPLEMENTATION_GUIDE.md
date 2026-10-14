# Triển khai TODO trong source chung

Giữ cấu trúc module trong `src/airbnb/`; không tạo một bộ source riêng theo tên thành viên.
Data check đã hoàn thành chạy độc lập và giữ nguyên. Phần phân tích cả kỳ vẫn là TODO.
Mỗi file ghi `OWNER`, `READY`, chữ ký hàm, mô tả kết quả và `TODO[TV1]` đến `TODO[TV5]`.
Các implementation AI trước đây vẫn có trong lịch sử Git và được khai báo trong AI_USAGE.

## Bắt đầu từ phần của mình

1. Tạo branch từ main mới nhất theo [Git workflow](GIT_WORKFLOW.md).
2. Đọc [TEAM](TEAM.md), module được giao và [CONTRACTS](CONTRACTS.md).
3. Viết xử lý trong hàm đã có; giữ tên hàm, tham số và các cột bắt buộc.
4. Tự tạo fixture nhỏ và test hàm, sau đó kiểm dữ liệu thật trong phạm vi nhóm.
5. Ghi lệnh/số liệu/giới hạn vào `reports/sections/tvN.md`; mở PR để review và merge.

Tìm `TODO[TV2]` trong editor để thấy việc của Đức; thay số tương ứng cho các thành viên khác.
Module còn làm dở giữ `READY = False` và báo `NotImplementedError` ở hàm chưa triển khai.
Chỉ bật `READY = True` khi mọi hàm mà pipeline dùng trong module đã có logic, test đạt và
reviewer xác nhận trong PR trước merge. Có thể merge PR một phần nhưng chưa bật READY.
Không trả dữ liệu giả/list rỗng hoặc chỉ đổi READY để vượt kiểm tra.

## Ví dụ Đức làm QA

Đức sửa `qa.clean_listings(records, snapshot, cfg)` trong `src/airbnb/qa.py`:

- `records` là iterator listing raw đã lọc theo workbook; đọc một lần, không giả định là list.
- `snapshot` là ngày YYYY-MM-DD; `cfg` là dict cấu hình.
- Trả `(cleaned_rows, qa_report_rows)` theo schema trong CONTRACTS.
- Không tự tải dữ liệu, sửa raw hoặc ghi kết quả chính trong hàm QA.

Tạo `tests/test_qa.py` kiểm các trường hợp có ý nghĩa: ID dài, giá thiếu trước mốc cuối,
kiểu sai/trùng/ngoại lai/danh mục lệch và tác động sau QA. Test có thể chuẩn bị đường import
như bộ tests hiện có: thêm `<gốc repo>/src` vào `sys.path` trước `from airbnb import qa`.

```bash
python -m unittest discover -s tests -p test_qa.py -v
python -m unittest discover -s tests -v
python run_pipeline.py --status
```

Test riêng của Đức chạy được dù Nam/Hiếu/Phan Huy còn TODO. Tương tự, Nam test trực tiếp
`calendar.aggregate`/`metrics`; Hiếu test `kpi.summarize`; Phan Huy test preprocessing,
JSON validation, baseline/evaluation và các lỗi API/cache. CI hiện dùng hàm giả cho phần
nối pipeline, nên owner phải bổ sung test thuật toán thực tế.

## Nhóm trưởng tích hợp qua import

Pipeline đã có các lời gọi sau (đoạn minh họa, không chạy độc lập):

```python
from airbnb import qa, calendar, reviews, kpi

cleaned, report = qa.clean_listings(raw_listings, snapshot, cfg)
calendar_rows, issues = calendar.aggregate(raw_calendar, snapshot, window_days, listing_ids)
review_issues = reviews.collect(raw_reviews, snapshot, review_map)
market_kpi = kpi.summarize(all_cleaned_listings, cfg)
```

Sau khi code đúng hàm/schema được merge, import tự dùng implementation mới. Nhóm trưởng
không phải thêm lại import sau từng PR và không chép logic thành viên vào `run_pipeline.py`.
Nhóm trưởng quản lý thứ tự gọi, gom kết quả và xuất CSV; từng owner quản lý thuật toán.

Nếu cần helper, có thể thêm một module nhỏ cùng package, ví dụ `calendar_helpers.py`, rồi
import từ `calendar.py`. Pipeline vẫn gọi `calendar.aggregate` như cũ. Nếu cần thêm bước
công khai mới, thống nhất chữ ký/cột, cập nhật CONTRACTS, import/lời gọi/writer và test tích hợp
trong PR. Tên/chữ ký đầu ra không đổi âm thầm.

Module chỉ định nghĩa hàm/hằng số khi import; không tải file, gọi API hoặc chạy pipeline ở cấp
module. Nếu cần script chạy riêng, đặt dưới `if __name__ == '__main__':` và có lệnh tái lập rõ.
Dùng relative import trong package, chẳng hạn `from .calendar_helpers import ...`.

## Bàn giao dữ liệu và hình

Hàm xử lý trả bảng/diagnostics; pipeline chung ghi CSV. Không dùng stdout làm đầu vào cho bước
sau. Terminal chỉ báo tiến độ và đường dẫn kết quả; không chép số liệu terminal vào notebook.
Hàm `viz_<phần>.render(tables, figures, cfg)` lưu hình trong `figures` được truyền vào và trả
`list[Path]`. Mỗi người dùng tên hình riêng để tránh ghi đè; `viz.py` chỉ điều phối.

Mỗi người tạo `reports/sections/tvN.md` gồm: mục tiêu/cách xử lý, lệnh chạy, đường dẫn file kết
quả, số liệu chính, phát hiện và giới hạn. Output phân tích tự sinh đang ignore; cung cấp lệnh
để người khác tạo lại. Bảng nhỏ cần commit và file báo cáo cuối do nhóm trưởng duyệt phạm vi.
Data check có luồng commit các CSV/notes nhỏ riêng, xem DATA_CHECK_WORKFLOW.

## Ràng buộc dữ liệu của nhóm

Loader đọc config/workbook, lọc listings/calendar theo 1.000 listing ID và reviews theo
5.000 review ID độc lập `listing_id`. ID giữ dạng chuỗi chính xác; calendar xử lý streaming.
Giá chỉ dùng mốc cuối; calendar không có giá để phân tích. Unavailable không chứng minh đã đặt.
Data check đếm từng mốc trước cleaning; phân tích reviews có thể dedupe giữa các mốc.

LLM nhận đúng 1.000 ID có dấu x ở Mẫu LLM. 100 dấu x ở Nhãn tay chọn các review cần gán nhãn,
không phải sentiment. Phan Huy tổ chức cả nhóm gán nhãn thật rồi lưu `review_id,sentiment`
vào `data/samples/manual_labels.csv`; sentiment là positive/mixed/negative.

`analysis_area` là vùng chữ nhật workbook, không phải `neighbourhood_cleansed`.
Hiếu và nhóm trưởng phải xác minh/ghi rõ phương án đáp ứng KPI neighbourhood khi cột thiếu;
contract hiện tại theo analysis_area chưa chứng minh đạt yêu cầu đó. Cohort cố định không
đủ để suy luận entry/exit toàn thị trường; TV1 cần điều chỉnh chỉ số/contract trước khi chốt.
Không lọc reviews thêm theo listing ID của nhóm; join phục vụ KPI phải báo tỷ lệ không ghép được.

## Lệnh chạy khi các module cần thiết đã hoàn thành

```bash
python run_pipeline.py --config configs/toronto.yaml --skip-llm
python run_pipeline.py --config configs/toronto.yaml --skip-llm --no-download
python run_pipeline.py --config configs/toronto.yaml
```

`--no-download` dùng raw local đã đủ cả CSV và GeoJSON; vẫn kiểm schema.
Lệnh đầy đủ cần workbook, raw, `GEMINI_API_KEY` và 100 nhãn sentiment thật. Không tự đọc `.env`.
`--skip-llm` bỏ API/evaluation/guest KPI/hình reviews; baseline/preprocessing vẫn cần hoàn thành.
Demo dùng fixture giả và chỉ hỗ trợ `--demo --skip-llm`; cũng bị chặn khi còn TODO.
Data check không phụ thuộc READY: vẫn chạy riêng bằng `scripts/check_data.py`.

Nếu thêm dependency, ghim phiên bản trong requirements và giữ pyproject đồng nhất nếu có khai
báo dependency tại đó. Khi gặp lỗi import sau pull, kích hoạt đúng `.venv` và cài lại requirements.
