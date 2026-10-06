# Nhóm 10 — Inside Airbnb Toronto

Bài tập lớn môn **Lập trình xử lý dữ liệu (UET.DSE2049)**, lớp **dse2049_1**, học kỳ 1 năm học **2026–2027**.
Nhóm có **5 thành viên**, cùng phát triển một pipeline phân tích Toronto qua bốn snapshot.

- **GitHub nhóm:** [2627-LTXLDL-Airbnb-dse2049_1-nhom10](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10)
- **Đề bài:** [Inside Airbnb — LTXLDL 2026–2027](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html)
- **Nguồn dataset Toronto:** [data.insideairbnb.com/canada/on/toronto/](https://data.insideairbnb.com/canada/on/toronto/)
- **Trang dữ liệu Inside Airbnb:** [Get the Data](https://insideairbnb.com/get-the-data/)
- **Kế hoạch và phân công của nhóm:** [docs/ORIGINAL_PLAN.md](docs/ORIGINAL_PLAN.md)

> **Trạng thái:** đây là bộ khung chung đã chạy demo và kiểm thử cơ bản, đang phát triển thành bài nộp.
> Chưa xác minh pipeline trên toàn bộ dữ liệu Toronto hoặc API Gemini thật; chưa có nhãn tay thật và báo cáo cuối.
> Demo là dữ liệu tổng hợp, không được sử dụng làm kết quả nghiên cứu Toronto.

## 1. Mục tiêu phân tích

Stakeholder dự kiến theo bản phân công: **Toronto Short-Term Rental & Tourism Market Monitoring Team**,
phục vụ theo dõi thị trường lưu trú và du lịch Toronto. Đây là bên liên quan do nhóm lựa chọn cho bài tập,
không phải tuyên bố có quan hệ đặt hàng thực tế.

Câu hỏi chính: **thị trường Airbnb Toronto thay đổi thế nào theo thời gian và neighbourhood về nguồn cung,
giá, availability, cấu trúc host và trải nghiệm khách hàng?**

Ba hướng phân tích: không gian, thời gian và trải nghiệm khách qua reviews/LLM.
Giá trong project sử dụng **CAD**. Calendar `unavailable` chỉ là trạng thái không sẵn có,
không đủ để kết luận đã được đặt hoặc suy ra occupancy.

## 2. Phân công code cho 5 người

Mỗi người phụ trách một module xuyên suốt **cả bốn snapshot**. Tất cả dùng cùng config,
contract dữ liệu và `run_pipeline.py`; không tách thành năm project riêng.
TV1–TV5 là ký hiệu theo tài liệu phân công; nhóm điền tên/MSSV thật trong [TEAM.md](docs/TEAM.md).

| Thành viên | Phạm vi và file chính | KPI / công việc phát triển | Reviewer |
|---|---|---|---|
| TV1 — nhóm trưởng | `run_pipeline.py`, `configs/toronto.yaml`, `src/airbnb/io.py`, `download.py`, `analysis.py` | Pipeline, tải dữ liệu, supply/churn, tích hợp, issues và merge PR | TV4 |
| TV2 | `src/airbnb/qa.py`, `eda.py`, `docs/QA.md`, `docs/CONTRACTS.md`, notebook `02_qa.ipynb` | QA, preprocessing, dictionary, tác động QA lên KPI | TV3 |
| TV3 | `src/airbnb/kpi.py`, phần spatial trong `viz.py`, notebook `03_listings_spatial.ipynb` | Giá, entire-home share, multi-listing host share, neighbourhood/maps | TV1 |
| TV4 | `src/airbnb/calendar.py`, notebook `04_calendar.ipynb` | Availability 30/90 ngày, weekday/weekend, tối ưu calendar lớn | TV5 |
| TV5 | `src/airbnb/reviews.py`, `llm.py`, `baseline.py`, `evaluate.py`, notebook `05_reviews_llm.ipynb` | Reviews, Gemini, cache, baseline, guest KPI, đánh giá và chi phí | TV2 |

`kpi.py` và `viz.py` hiện là nơi tổng hợp có nhiều người liên quan: mỗi PR chỉ sửa hàm thuộc nhiệm vụ,
trao đổi owner trước khi sửa chung. Khi mở rộng, tách `viz_spatial.py`, `viz_calendar.py`, `viz_reviews.py`
để từng người có file riêng; TV1 tích hợp lời gọi vào pipeline.

Công việc chung: **200 review được gán nhãn tay, 40 review/người**; TV5 tổ chức chọn mẫu,
hướng dẫn nhãn và tổng hợp. Từng người viết `reports/sections/tvN.md` và test phần mình.
Mỗi PR có reviewer khác tác giả. Tất cả phải giải thích được toàn bộ sản phẩm khi vấn đáp.
Chi tiết: [TEAM.md](docs/TEAM.md), [CONTRACTS.md](docs/CONTRACTS.md).

## 3. Dataset Toronto và 4 snapshot bắt buộc

Config ở [configs/toronto.yaml](configs/toronto.yaml): `city = toronto`,
`data_root = canada/on/toronto`, `currency = CAD`.
Bốn ngày trong config khớp bản phân công và danh sách Toronto trong đề bài:
**2025-09-11, 2025-11-11, 2026-03-19, 2026-06-15**.

Mỗi snapshot tải **4 file chi tiết**, tổng cộng **16 file**:

| File | Nội dung | Khóa phân tích |
|---|---|---|
| `data/listings.csv.gz` | Listing, host, giá, room type, neighbourhood, tọa độ | `(snapshot_date, listing_id)`; raw `id` đổi thành `listing_id` |
| `data/calendar.csv.gz` | Ngày và trạng thái availability theo listing | `(snapshot_date, listing_id, date)` |
| `data/reviews.csv.gz` | Review văn bản cho baseline/LLM | raw `id` đổi thành `review_id`, dedupe toàn bộ snapshot |
| `visualisations/neighbourhoods.geojson` | Ranh giới neighbourhood | Khảo sát trường tên khu vực khi join với listings |

### Link tải đầy đủ

Các URL dưới đây được dựng theo quy tắc của đề bài và giống URL mà `download.py` sử dụng.
Không thay file `.csv.gz` chi tiết bằng file CSV summary ở thư mục `visualisations`.
Trang gốc Toronto có thể không cung cấp trang liệt kê; khi tải, dùng URL từng file cụ thể.

**Kiểm tra ngày 06/10/2026:** cả 16 URL bên dưới trả về **HTTP 200** qua HEAD.
Đây là kiểm tra truy cập file, chưa kiểm nội dung/schema hoặc tải đủ dữ liệu.

| Snapshot | Listings | Calendar | Reviews | Neighbourhoods |
|---|---|---|---|---|
| 2025-09-11 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/visualisations/neighbourhoods.geojson) |
| 2025-11-11 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-11-11/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-11-11/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-11-11/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2025-11-11/visualisations/neighbourhoods.geojson) |
| 2026-03-19 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/visualisations/neighbourhoods.geojson) |
| 2026-06-15 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/visualisations/neighbourhoods.geojson) |

Nguồn: **Inside Airbnb**, giấy phép **CC BY 4.0** theo đề bài. Báo cáo phải ghi nguồn và ngày snapshot.
Không commit raw lên GitHub. Clone/pull lấy code và samples; mỗi thành viên tải raw bằng script trên máy mình.
Thay snapshot để kiểm thử chỉ sửa config, không sửa ngày trong source.

## 4. Cấu trúc repository chung

```text
.
├── configs/toronto.yaml
├── data/
│   ├── raw/<YYYY-MM-DD>/        # script tạo; gitignore
│   │   ├── listings.csv.gz
│   │   ├── calendar.csv.gz
│   │   ├── reviews.csv.gz
│   │   └── neighbourhoods.geojson
│   ├── processed/demo|real/     # cleaned, kpi_*.csv, baseline và LLM
│   └── samples/                # fixture demo và nhãn tay
├── src/airbnb/                 # modules của 5 thành viên
├── notebooks/                  # khám phá; không phải pipeline chính
├── scripts/download_data.py
├── tests/test_pipeline.py
├── figures/demo|real/          # hình sinh tự động
├── reports/
│   ├── generated/demo|real/    # QA, EDA, evaluation, run metadata
│   ├── qa_report.csv           # pipeline thật tạo
│   └── sections/               # mỗi người một phần báo cáo
├── docs/                       # phân công, Git, contract, QA, KPI, backlog
├── .github/                    # CI + mẫu PR
├── .python-version
├── .env.example
├── .gitignore
├── AI_USAGE.md
├── requirements.txt
├── pyproject.toml
└── run_pipeline.py
```

`src/airbnb/` là package chứa các module tương ứng gợi ý `src/` của đề bài.
Thư mục raw/processed/figures rỗng hoặc bị ignore có thể không xuất hiện sau clone;
pipeline tự tạo khi chạy. Logic tái sử dụng đặt trong source, không chỉ ở notebook.

## 5. Clone, cài môi trường và chạy thử

Sau khi leader đưa bộ khung lên `main`, thành viên clone lần đầu:

```bash
git clone https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10.git
cd 2627-LTXLDL-Airbnb-dse2049_1-nhom10
```

Repo theo đề cần để **private**; tài khoản clone phải được cấp quyền. Địa chỉ trên lấy từ
remote `origin` của repo hiện tại; quyền truy cập, protection và trạng thái remote cần nhóm kiểm tra trên GitHub.

Python đã chạy thử: **3.13.7**, ghi ở [.python-version](.python-version).
Pipeline hiện chỉ dùng thư viện chuẩn Python; `requirements.txt` không có dependency runtime.
`pyproject.toml` chứa metadata và build backend ghim; cài editable package là tùy chọn, cần mạng để tải backend.
Nếu thêm pandas/Polars/thư viện khác, ghim `==` trong requirements và kiểm thử môi trường sạch.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_pipeline.py --config configs/toronto.yaml --demo --skip-llm
python -m unittest discover -s tests -v
```

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_pipeline.py --config configs/toronto.yaml --demo --skip-llm
python -m unittest discover -s tests -v
```

Demo không cần mạng hoặc API key, có 4 snapshot tổng hợp, 3 listing/mốc,
90 ngày/listing và 3 review duy nhất. Kết quả ở `data/processed/demo/`,
`reports/generated/demo/`, `figures/demo/`; tuyệt đối không dùng làm số liệu Toronto.
Notebook là placeholder khám phá; Jupyter không cần thiết để chạy pipeline.

## 6. Pipeline dữ liệu thật

### Tải và chạy các bước chưa dùng LLM

```bash
python run_pipeline.py --config configs/toronto.yaml --skip-llm
```

Lệnh tự tải file thiếu, kiểm schema, làm sạch, tổng hợp calendar/reviews,
tính KPI và baseline, rồi sinh hình. Raw lưu tại `data/raw/<snapshot>/`.
Muốn chỉ tải hoặc dùng file đã tải:

```bash
python scripts/download_data.py configs/toronto.yaml
python run_pipeline.py --config configs/toronto.yaml --no-download --skip-llm
```

`--no-download` yêu cầu đủ các file raw; vẫn kiểm schema. Downloader tải tuần tự,
lưu manifest URL/dung lượng/SHA256 ở `reports/generated/download_manifest.csv`.
Dữ liệu calendar lớn; cần đo RAM/thời gian trên dữ liệu thật và tối ưu theo phân công TV4.

### Chạy toàn bộ, gồm LLM

Đặt khoá Gemini trong biến môi trường **`GEMINI_API_KEY`** trên terminal hiện tại:

```bash
# macOS / Linux
export GEMINI_API_KEY='YOUR_API_KEY'
python run_pipeline.py --config configs/toronto.yaml
```

```powershell
# Windows PowerShell
$env:GEMINI_API_KEY='YOUR_API_KEY'
python run_pipeline.py --config configs/toronto.yaml
```

`.env.example` chỉ mô tả tên biến; code **không tự đọc `.env`**.
Không lưu key thật trong source, config, notebook hoặc commit.
Model, taxonomy, seed, cỡ mẫu, retry và cache nằm trong config.
Adapter gửi comments tới Gemini, có cache theo model + prompt + text, kiểm JSON và retry lỗi cơ bản.
Cần kiểm tra model/quota và xác minh API thật trước nộp.

Config `.yaml` hiện dùng **cú pháp JSON hợp lệ trong YAML** để không cần YAML parser;
giữ dấu ngoặc và dấu nháy khi sửa. Các path tương đối tính từ gốc repo.
Cỡ mẫu hiện **20** chỉ để phát triển; chưa đủ đánh giá trên ≥100 nhãn tay theo đề.
Nhóm cần chọn mẫu thật, tăng cỡ mẫu, bảo đảm ≥100 review có cả nhãn tay và dự đoán cho cả hai phương pháp.
`data/samples/manual_labels.csv` hiện chỉ có header `review_id,sentiment`.
Nhãn hợp lệ: `positive`, `mixed`, `negative`.

`--skip-llm` không gọi API, xuất file LLM/guest KPI chỉ có header và ghi `llm_status=skipped`.
Chế độ này phục vụ phát triển; trước nộp phải kiểm thử lệnh đầy đủ có LLM thật.
Muốn kiểm thử gọi API mới thay vì dùng cache, sao lưu rồi đổi path cache trong config.

## 7. Output để đối chiếu

| Output | Nội dung |
|---|---|
| `data/processed/real/listings.csv` | Listing sạch, giá CAD, khóa snapshot/listing, `qa_flags` |
| `data/processed/real/calendar_summary.csv` | Available/observed/expected days và availability rate |
| `data/processed/real/reviews.csv` | Reviews dedupe, `first_seen_snapshot` |
| `data/processed/real/kpi_market.csv` | Supply, median price, entire-home share, host share, availability theo snapshot + area |
| `data/processed/real/kpi_churn.csv` | New/retained/disappeared, entry/exit rates |
| `data/processed/real/baseline.csv` | Baseline sentiment bằng keyword tiếng Anh |
| `data/processed/real/llm_reviews.csv` | Sentiment, language, positive/negative aspects từ LLM |
| `data/processed/real/kpi_guest.csv` | Tỷ lệ mixed/negative trong mẫu LLM |
| `reports/qa_report.csv` | QA thật: số dòng chịu tác động; median giá trước/sau cho listings |
| `reports/generated/real/` | Bản QA, `eda_flags.csv`, `evaluation.csv`, `run_metadata.json` |
| `figures/real/` | `supply.svg`, `price.svg`, `spatial.svg`, `llm_sentiment.svg` khi có LLM |

Demo dùng cùng tên output dưới thư mục `demo/`, không ghi đè `reports/qa_report.csv`.
QA ưu tiên flag anomaly; loại khóa thiếu/trùng, bỏ giá invalid/outlier khỏi median.
Guest KPI hiện là **tỷ lệ trong mẫu**, chưa phải ước lượng toàn thị trường.
Spatial SVG hiện là hình vị trí và ranh giới sơ bộ, chưa là choropleth/density map hoàn chỉnh.
KPI nằm dưới `data/processed/real/`; trước nộp cần thống nhất layout với cách kiểm output của giảng viên
(nếu yêu cầu trực tiếp `data/processed/kpi_*.csv`, xuất thêm các file tương ứng tại đó).

## 8. Quy trình chung: main → branch → PR → merge → pull

`main` chứa phiên bản tích hợp của cả nhóm. Pull lấy **code đã commit và push lên remote**,
không lấy thay đổi chưa commit trên máy leader, raw data hoặc API key.

### Leader đưa bộ khung hiện tại lên GitHub

Repo hiện đã có `origin` đúng địa chỉ nhóm và branch `main`, không cần `git init` hoặc thêm origin lần nữa.
Kiểm tra file trước khi commit; `.gitignore` loại raw, outputs, môi trường và secret.

```bash
git switch main
git status --short
git add README.md AI_USAGE.md configs data docs notebooks pyproject.toml requirements.txt run_pipeline.py scripts src tests .gitignore .python-version .env.example .github
# git add data chỉ thêm samples/docs; raw và processed output bị ignore
git diff --cached --stat
git commit -m "chore: add shared Toronto starter for group 10"
git push origin main
```

Đây là hướng dẫn lần đưa khung lên main của nhóm trưởng. Sau đó dùng PR cho các task;
nếu main đã được bảo vệ, đưa khung lên một branch `chore/group10-starter` và mở PR thay direct push.
Kiểm tra GitHub để mời đủ 5 người và giảng viên, giữ repo private, yêu cầu reviewer và CI pass.

### Thành viên làm task

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/tv2-qa-price
# phát triển module, chạy test + demo
python -m unittest discover -s tests -v
python run_pipeline.py --demo --skip-llm
git add src/airbnb/qa.py tests/ docs/QA.md
git commit -m "feat(qa): flag invalid nightly prices"
git push -u origin feat/tv2-qa-price
```

Mở PR vào `main` trên GitHub, ghi thay đổi/input/output/cách kiểm chứng.
Reviewer khác tác giả duyệt, CI pass, leader hoặc người được phân quyền merge.
Sau merge, mọi người cập nhật code:

```bash
git switch main
git pull --ff-only origin main
# tạo branch mới cho task tiếp theo
```

Trước đổi branch/pull, commit công việc đang làm hoặc lưu bằng stash nếu cần.
Cập nhật branch đang làm bằng `git fetch origin` rồi `git merge origin/main`;
đọc và giải conflict với owner, chạy lại test/demo rồi push. Không force-push branch chung.

Giảm conflict: mỗi task một branch/PR nhỏ, dùng file owner, mỗi người một notebook và report section;
đổi config/schema/output cần trao đổi TV1 và người dùng dữ liệu downstream trước merge.
Chi tiết: [GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).

## 9. Đối chiếu đề bài và phần còn thiếu

Đề bài là chuẩn yêu cầu; kế hoạch nhóm bổ sung mục tiêu 200 nhãn, 15–20 QA rule và 6–8 hình.
Cấu trúc hiện phù hợp để phát triển nhưng **chưa xác nhận đáp ứng đầy đủ bài nộp**.

| Nội dung | Hiện trạng | Việc còn lại |
|---|---|---|
| Pipeline một lệnh, config thành phố/ngày | Có, demo đã kiểm thử | Chạy dữ liệu thật và snapshot mới |
| Bốn snapshot Toronto và downloader | Config/URL đủ 4 mốc × 4 file | Tải đủ và kiểm dữ liệu thật |
| QA và tác động lên KPI | Rule cơ bản, report, median trước/sau | Schema drift, địa lý, integrity và impact đầy đủ |
| 5–8 KPI, khu vực/thời gian, tiền tệ | Khung 7 nhóm KPI, CAD, area/time | Kiểm số liệu, room type, denominator/coverage |
| LLM, baseline, accuracy/F1 | Có adapter/cache/baseline/evaluation | ≥100 paired nhãn thật, API thật, error analysis, chi phí |
| Hình không gian/thời gian/LLM | Có SVG khung | Hoàn thiện 6–8 hình theo kế hoạch và insight thật |
| Môi trường, AI_USAGE, Git | Có file setup, AI_USAGE, CI và hướng dẫn | Ghim thêm thư viện khi bổ sung; cấu hình GitHub thực tế |
| Báo cáo PDF ≤10 trang | Chưa có | Viết report, nguồn/ngày snapshot, commit đã nộp |

Trước nộp: clone vào thư mục mới, dựng môi trường theo README, chạy pipeline thật có API key khác,
đối chiếu KPI/hình với báo cáo và thử snapshot khác bằng config. Cập nhật [AI_USAGE.md](AI_USAGE.md)
với prompt, lỗi AI và cách nhóm kiểm chứng thực tế.
Xem việc từng người cần hoàn thành tại [ROADMAP.md](docs/ROADMAP.md), [QA.md](docs/QA.md), [KPI.md](docs/KPI.md).
Sau khi kiểm chứng bản cuối, ghi commit vào báo cáo rồi tạo/push tag `final` theo đề bài.
