# Inside Airbnb Toronto — Nhóm 10

Bài tập lớn Lập trình xử lý dữ liệu, **UET.DSE2049 1**, học kỳ 1 năm 2026–2027.
Mã dữ liệu: **DSE2049-C01-G10-toronto**. Tiền tệ: **CAD**.

[GitHub nhóm](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10)
· [Đề bài hiện hành](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html)
· [Nguồn Toronto](https://data.insideairbnb.com/canada/on/toronto/)

## Bản chuẩn bị nộp ngày 2026-11-22

Pipeline đã tích hợp code của năm thành viên. Repo có cache Gemini cho đủ **1.000 review** và giữ nguyên **100 nhãn tay**.
Kết quả trên cùng 100 nhãn tay:
Gemini accuracy 96%, macro-F1 0,8594; baseline 95% và 0,8278. Gemini chỉ nhận đúng 3/7 review mixed,
nên không dùng riêng accuracy để tuyên bố mô hình vượt trội ở mọi lớp.

[Tải PDF báo cáo chính](reports/Nhom10_InsideAirbnb_Report.pdf) · [Cách sửa và tái tạo PDF](reports/README.md)

PDF có 9 trang. Nhóm trưởng điền hai MSSV còn trống và có thể thêm một trang bìa theo mẫu Viện.
Mốc **2025-12-12 đã được nhóm trưởng xác nhận với giảng viên**. Xem [checklist nộp và tag `final`](docs/FINAL_CHECKLIST.md).
Xem [hướng dẫn cache](docs/LLM_CACHE.md) để biết cách chuẩn bị lại nếu đổi model/prompt/text.

Bên nhận phân tích giả định: nhóm theo dõi lưu trú ngắn hạn và du lịch Toronto. Mục tiêu là theo dõi
cơ cấu nguồn cung trong cohort được giao, mức giá cuối kỳ, lịch sẵn có và vấn đề trải nghiệm khách.
Không suy rộng biến động của cohort thành gia nhập/rời thị trường toàn Toronto.

## Cài đặt và chạy

Python đã kiểm thử: **3.13.7** (`.python-version`). Các thư viện trực tiếp được ghim `==` trong
`requirements.txt`; `pyproject.toml` đọc chính tệp này khi cài package.

```bash
git clone https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10.git
cd 2627-LTXLDL-Airbnb-dse2049_1-nhom10
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell: `py -3.13 -m venv .venv`, sau đó `.venv\Scripts\Activate.ps1`.
Repo riêng tư cần quyền truy cập GitHub của nhóm.

**Chạy toàn bộ bằng cache có sẵn trong repo**

```bash
python run_pipeline.py --config configs/toronto.yaml
```

Lệnh tải những raw file còn thiếu theo config, đọc tập ID chính thức, QA → KPI → baseline → cache LLM →
đánh giá trên 100 nhãn tay → xuất CSV và hình. Không đọc `.env`, không gọi Gemini.
Nếu raw đã đủ, thêm `--no-download` để không dùng mạng tải dữ liệu.

Các lệnh kiểm tra riêng gồm chế độ không LLM, demo, trạng thái module và kiểm thử:

```bash
python run_pipeline.py --config configs/toronto.yaml --skip-llm --no-download
python run_pipeline.py --demo --skip-llm
python run_pipeline.py --status
python -m pytest -q
```

Demo là dữ liệu giả để kiểm thử, không dùng số liệu đó cho báo cáo thật. Test không gọi Gemini.
Các lỗi dữ liệu, cache hoặc thiếu thư viện phải được xử lý; không dùng ảnh thay thế không có dữ liệu.

## Thành viên và module

| Người | Phần phụ trách trong `src/airbnb/` | Bàn giao |
|---|---|---|
| TV1 — Dương Nhật Huy, nhóm trưởng | `pipeline.py`, loading/config/download, `analysis.py`, `viz_market.py` | Tích hợp, coverage cohort, biến động host/room, báo cáo chung |
| TV2 — Mai Anh Đức | `qa.py`, `eda.py`, `viz_qa.py` | QA, dữ liệu thiếu, schema/category drift, tác động trước/sau QA |
| TV3 — Nguyễn Quốc Hiếu | `kpi.py`, `viz_spatial.py` | KPI nguồn cung/giá/phòng/host và không gian |
| TV4 — Vũ Phạm Khánh Nam | `calendar.py`, `viz_calendar.py` | Availability và coverage lịch theo thời gian/vùng |
| TV5 — Phan Ngọc Huy | `reviews.py`, `baseline.py`, `llm.py`, `evaluate.py`, `review_kpi.py`, `viz_reviews.py` | Review, cache Gemini, đánh giá, guest KPI |

Mỗi người xử lý phần mình trên **cả các mốc**, không chia mỗi người một snapshot.
Code chung nằm trong package; không tạo bản sao source theo tên người rồi chép vào `main`.
Các file `viz_*` là module vẽ của từng mảng; giữ chúng để chia trách nhiệm và tránh xung đột.
`viz.py` chỉ gọi các module này, không chứa bản sao công thức KPI.

```text
run_pipeline.py                 CLI: nhận tham số, gọi luồng chung
src/airbnb/pipeline.py           Điều phối module, kiểm tra, xuất kết quả
src/airbnb/outputs.py            Hợp đồng CSV dùng chung
src/airbnb/labels.py             Chỉ đọc/kiểm nhãn tay
src/airbnb/{qa,kpi,calendar,...}  Thuật toán theo phần việc
configs/                        Thành phố, mốc, đường dẫn, giá, taxonomy
scripts/                        Các lệnh độc lập, tải dữ liệu, data check, tạo cache
notebooks/                      Khám phá tùy chọn, không thay luồng chung
tests/                          Fixture giả + kiểm thử tích hợp không API
data/reference/assignment.json  Chỉ phạm vi nhóm xuất từ workbook, ID dạng chuỗi
data/assignments/assignment.xlsx Workbook gốc cục bộ, gitignore
data/raw/YYYY-MM-DD/            File nguồn, gitignore, không sửa
data/processed/                 Cache cần commit; các CSV sinh ra được gitignore
reports/checks/                 Báo cáo kiểm tra đầu vào ban đầu, giữ nguyên
reports/Nhom10_InsideAirbnb_Report.pdf  PDF chính để nộp
reports/generated/              QA, đánh giá, metadata của các lần chạy
reports/sections/               Phần báo cáo của từng thành viên
figures/                        Hình sinh tự động
```

`reports/data_dictionary.csv` và `reports/qa_rule_catalog.csv` là bản mô tả chuẩn duy nhất.
Các script cũ `check_calendar.py`/`check_listings.py` chuyển tiếp sang data check chung;
không còn đường dẫn máy cá nhân hoặc danh sách 1.000 ID ghi cứng trong code.

## Dữ liệu và quy tắc phạm vi

Bốn mốc **trong workbook của nhóm**:

| Mốc | Ngày | Listings | Calendar | Reviews | GeoJSON |
|---|---|---|---|---|---|
| 1 | 2025-09-11 | [gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/listings.csv.gz) | [gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/calendar.csv.gz) | [gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/reviews.csv.gz) | [json](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/visualisations/neighbourhoods.geojson) |
| 2 | 2025-12-12 | [gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/listings.csv.gz) | [gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/calendar.csv.gz) | [gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/reviews.csv.gz) | [json](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/visualisations/neighbourhoods.geojson) |
| 3 | 2026-03-19 | [gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/listings.csv.gz) | [gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/calendar.csv.gz) | [gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/reviews.csv.gz) | [json](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/visualisations/neighbourhoods.geojson) |
| 4 | 2026-06-15 | [gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/listings.csv.gz) | [gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/calendar.csv.gz) | [gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/reviews.csv.gz) | [json](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/visualisations/neighbourhoods.geojson) |

Mốc thứ hai dùng **2025-12-12 theo workbook và xác nhận của giảng viên qua nhóm trưởng**;
không thay bằng ngày trên danh sách thành phố chung. Bốn mốc được giữ đúng như bảng trên.

- Listings và calendar lọc theo **1.000 listing_id**. Calendar đọc streaming, không nạp cả thành phố vào RAM.
- Reviews lọc độc lập theo **5.000 review_id/mốc**, không dùng listing_id để lọc reviews.
- Tập LLM **1.000**, tập nhãn tay **100** lấy trực tiếp dấu trong workbook, không lấy mẫu lại.
- ID luôn là chuỗi; không mở rồi lưu workbook/CSV nguồn bằng Excel vì có ID dài 18–19 chữ số.
- Nếu có workbook cục bộ, pipeline đọc workbook; nếu không có, đọc manifest phạm vi nhóm đã commit.
  Manifest có mã băm workbook gốc; không chứa dữ liệu của các nhóm khác. Không tự sửa danh sách ID.
- Giá phân tích chỉ dùng `price_snapshot=2026-06-15` từ **listings**. Giá thiếu ở các mốc trước không
  phải lý do xin cấp lại dữ liệu. Calendar không có giá; unavailable không đồng nghĩa đã có khách đặt.
- `analysis_area` A01–A08 là vùng chữ nhật của bài giao, khác `neighbourhood_cleansed` từ Inside Airbnb.
- Review trùng qua các mốc giữ một ID; `first_seen_snapshot` và `date` review có ý nghĩa khác nhau.
- Nguồn Inside Airbnb, CC BY 4.0. Ghi ngày từng mốc và nguồn trong báo cáo.

Để chạy thêm mốc **không LLM**, sửa danh sách `snapshots` trong config (ngày ISO, tăng dần), giữ mã nhóm,
ID và `price_snapshot`, rồi chạy lại `--skip-llm`. Có thể thêm `2025-11-11` giữa hai mốc đầu hoặc dùng config
chỉ chứa mốc mới để kiểm tra. Đổi `paths.raw` nếu dữ liệu ở ổ khác. Không cần sửa source/GeoJSON path.
Giữ đủ bốn mốc được giao trong config dùng để tạo cache và chạy đánh giá cuối cùng.

## Kết quả sau khi chạy

| Chế độ | CSV dữ liệu/KPI | QA, metadata, đánh giá | Hình |
|---|---|---|---|
| Đầy đủ từ cache | `data/processed/real/` | `reports/generated/real/` | `figures/real/` |
| Không LLM | `data/processed/real/non_llm/` | `reports/generated/real/non_llm/` | `figures/real/non_llm/` |
| Demo | `data/processed/demo/` | `reports/generated/demo/` | `figures/demo/` |

`--skip-llm` không ghi CSV LLM/evaluation/guest rỗng lên kết quả đầy đủ.
Các bảng và hình được chuẩn bị tại thư mục tạm; chỉ xuất khi module xử lý và vẽ thành công.
Metadata ghi config, SHA256 đầu vào, số dòng và danh sách artifact. Dùng các tệp trong metadata của lần chạy đó;
không trộn hình cũ, CSV từ notebook hoặc hai chế độ vào một báo cáo.

Các bảng chính: `listings.csv`, `calendar_summary.csv`, `reviews.csv`, `baseline.csv`,
`kpi_market.csv` (mốc × analysis_area), `kpi_neighbourhood.csv` (mốc × neighbourhood),
`kpi_calendar.csv`, `kpi_cohort.csv`, `kpi_churn.csv`; chế độ đầy đủ thêm `llm_reviews.csv`, `kpi_guest.csv`.
Lần chạy đầy đủ cũng xuất các bảng KPI vào `data/processed/kpi_*.csv` theo đường dẫn chấm của đề.
QA xuất `qa_report.csv`, `qa_missingness.csv`, `qa_kpi_impact.csv`, `eda_flags.csv`;
đánh giá xuất `evaluation.csv` trên cùng 100 nhãn thật cho baseline và Gemini.
Bản `reports/qa_report.csv` ở gốc là bản QA của lần chạy thật gần nhất.

KPI trọng tâm: supply, median price/price_n, entire-home share, tỷ lệ listing thuộc host nhiều listing
trong cohort, availability/coverage lịch, coverage cohort và guest issue rate.
Giá ngoài mốc được phép dùng để trống; mẫu số 0 được thể hiện là không xác định.
Guest KPI theo vùng chỉ dùng review nối được với cohort listing và có chỉ số join coverage riêng.
Bản đồ HTML có thể cần Internet để tải thư viện/nền bản đồ khi mở; CSV và hình PNG/SVG vẫn được sinh cục bộ.

## Kiểm hoặc tạo lại cache Gemini — TV5/nhóm trưởng

Cache trong repo đủ để chấm. Nếu cần tạo lại vì thay model, prompt hoặc mẫu, đọc taxonomy/prompt trong
`src/airbnb/llm.py`. Script tạo cache nhận `GEMINI_API_KEY` từ môi trường hoặc `.env` cục bộ đã được gitignore.

```bash
python scripts/generate_llm_cache.py --config configs/toronto.yaml
python scripts/generate_llm_cache.py --config configs/toronto.yaml --check
python run_pipeline.py --config configs/toronto.yaml --no-download
```

Lệnh đầu **có gọi Gemini**, sử dụng hạn mức/tính phí của tài khoản. Cache ghi sau từng review để có thể chạy tiếp.
`--check` và pipeline chính chỉ đọc cache, không gọi API ngay cả khi có key.
Cache lưu review_id, hash text, model, prompt, taxonomy và kết quả JSON đã kiểm tra schema;
đổi một trong các yếu tố đó thì cache cũ không được dùng thay thế.
Sau khi kiểm đủ 1.000 kết quả thật, commit **chỉ** `data/processed/llm_cache.jsonl` (đã có ngoại lệ gitignore).
Không lấy nhãn tay hoặc baseline đóng giả kết quả Gemini. Không commit CSV raw hay khóa API.

## Data check và nhãn tay

Luồng kiểm tra dữ liệu ban đầu vẫn riêng và dùng workbook gốc:

```bash
python scripts/check_data.py --part listings
python scripts/check_data.py --part listing-details
python scripts/check_data.py --part calendar
python scripts/check_data.py --part reviews
python scripts/check_data.py --part merge
```

Chạy `--part all` nếu nhóm trưởng muốn tạo lại toàn bộ. Lệnh này ghi lại `reports/checks/`;
khi đối chiếu lịch sử, dùng config có `output` khác. Hai bảng thành phần lịch sử có fingerprint workbook khác
bản hiện tại; cần chạy lại trước khi merge data check mới. Số liệu và SHA256 file raw đã được so khớp trong biên bản.
Câu 2 của báo cáo data check là **1.000/100 từ workbook**, khác việc đã chạy Gemini hay chưa.

[Hướng dẫn nhãn tay](docs/MANUAL_LABELING.md) và [phiếu cá nhân](data/samples/labeling/README.md)
được giữ để truy xuất nguồn gốc. Cả 100 nhãn hiện có đã được kiểm tra; không gán lại hoặc sửa để tăng điểm mô hình.

## Branch → PR → main

```bash
git switch main
git pull --ff-only origin main
git switch -c ten-ban/phan-viec
# Sửa module được giao và test tương ứng
python -m pytest -q
git add <cac-file-da-kiem-tra>
git commit -m "Mô tả thay đổi và lý do"
git push -u origin ten-ban/phan-viec
```

Mở PR vào `main`, ghi cách chạy, kết quả, giới hạn; reviewer kiểm trước khi merge.
Sau merge, mọi người pull lại `main` để nhận code mới. Không gửi ảnh terminal thay code/CSV;
không sửa đồng thời file nhãn tay hoặc config chung khi chưa thống nhất.
Xem [Git workflow](docs/GIT_WORKFLOW.md), [hợp đồng hàm/bảng](docs/CONTRACTS.md),
[checklist hiện tại](docs/FINAL_CHECKLIST.md), [minh bạch AI](AI_USAGE.md).
Notebook chỉ phục vụ giải thích/khám phá; sản phẩm nộp phải tái tạo được bằng lệnh chung.
