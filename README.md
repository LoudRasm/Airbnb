# Nhóm 10 Inside Airbnb Toronto

Bài tập lớn Lập trình xử lý dữ liệu, lớp **UET.DSE2049 1**, nhóm **10**, học kỳ 1 năm 2026–2027.
[GitHub nhóm](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10)
· [Đề bài](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html)

## Trạng thái hiện tại

Repo giữ cấu trúc **module trong `src/airbnb/`**. Đây là source chung: mỗi thành viên sửa
file được giao trên branch riêng, mở PR vào `main`; sau merge, pipeline import code mới.
Không cần folder theo tên người hoặc chép code sang một bộ source khác.

**Repo có hai phần:**

| Phần | Trạng thái | Lệnh |
|---|---|---|
| Kiểm tra dữ liệu đầu vào theo workbook | Đã chạy trên dữ liệu thật; giữ nguyên | `python scripts/check_data.py --part ...` |
| QA, EDA, KPI, LLM và hình cho bài cả kỳ | **Khung TODO**, mỗi người tự triển khai phần mình | `python run_pipeline.py --status` |

Các module phân tích đã được trả về khung có chữ ký hàm, hướng dẫn đầu vào/đầu ra và
`TODO[TV1]` đến `TODO[TV5]`. Có `READY = False` và `NotImplementedError` để tránh hiểu nhầm
khung trống là kết quả hoàn thành. Code cũ vẫn có trong lịch sử Git; không dùng nó làm đóng góp
triển khai của các thành viên. [Hướng dẫn triển khai và import](docs/IMPLEMENTATION_GUIDE.md).

## Thành viên và phần code cả kỳ

| Người | File tự triển khai | Reviewer |
|---|---|---|
| TV1 — Dương Nhật Huy | `run_pipeline.py`, `loading.py`, config/download, `analysis.py`, `viz_market.py` | Nam |
| TV2 — Mai Anh Đức | `qa.py`, `eda.py`, `viz_qa.py` | Hiếu |
| TV3 — Nguyễn Quốc Hiếu | `kpi.py`, `viz_spatial.py` | Nhóm trưởng |
| TV4 — Vũ Phạm Khánh Nam | `calendar.py`, `viz_calendar.py` | Phan Huy |
| TV5 — Phan Ngọc Huy | `reviews.py`, `baseline.py`, `llm.py`, `evaluate.py`, `review_kpi.py`, `viz_reviews.py` | Đức |

Các tên file trên nằm trong `src/airbnb/`. Mỗi người làm module cho **cả 4 mốc**, không chia
mỗi người một mốc. Mỗi người viết test phù hợp và phần báo cáo riêng. [Phân công chi tiết](docs/TEAM.md).

## Cấu trúc và tài liệu cần đọc

```text
configs/                 Cấu hình Toronto và kiểm tra đầu vào
data/raw/<YYYY-MM-DD>/   Dữ liệu gốc của từng mốc, gitignore
data/assignments/        Workbook gốc giữ trên mỗi máy, gitignore
data/samples/            Fixture giả và manual_labels.csv chờ nhãn thật
data/processed/          Bảng sạch, kết quả LLM và KPI do pipeline sinh
src/airbnb/              Module chung; TODO và OWNER ghi ngay trong file
scripts/                Lệnh tải dữ liệu và kiểm tra đầu vào
tests/                  Kiểm thử nền và kiểm thử do từng thành viên bổ sung
figures/                Hình do pipeline sinh
reports/checks/         CSV, ghi chú và chẩn đoán data check đã hoàn thành
reports/generated/      Báo cáo thống kê do pipeline phân tích sinh
reports/sections/       Mỗi người tự tạo tvN.md để bàn giao phần báo cáo
notebooks/              Khám phá tùy chọn; không thay luồng chạy chung
run_pipeline.py         Điều phối import → xử lý → xuất file
```

| Cần làm | Đọc |
|---|---|
| Biết phần của mình và kết quả phải bàn giao | [TEAM.md](docs/TEAM.md) |
| Triển khai TODO, giữ đầu vào/đầu ra và nối import | [IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md), [CONTRACTS.md](docs/CONTRACTS.md) |
| Tạo branch, push, mở PR, merge và pull lại | [GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md) |
| Chạy lại kiểm tra dữ liệu hoặc tổng hợp CSV nộp | [DATA_CHECK_WORKFLOW.md](docs/DATA_CHECK_WORKFLOW.md) |
| Theo dõi việc còn thiếu trước bài cuối | [ROADMAP.md](docs/ROADMAP.md) |

Sơ đồ trong đề gợi ý tên module bên trong `src/`; repo đặt chúng trong package `airbnb`
để import ổn định. Những thư mục và file bàn giao ở gốc vẫn giữ theo đề.

## Cài môi trường và cập nhật code

Python đã kiểm thử: **3.13.7**, xem `.python-version`. Khung dùng Python stdlib;
không cần pandas để chạy data check chung. Nếu thêm thư viện cho phần mình, ghim `==` trong
`requirements.txt`; nếu khai báo trong `pyproject.toml` thì giữ hai nơi đồng nhất.

```bash
git clone https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10.git
cd 2627-LTXLDL-Airbnb-dse2049_1-nhom10
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows PowerShell: dùng `py -3.13 -m venv .venv` và `.venv\Scripts\Activate.ps1`.
Repo cần quyền truy cập GitHub của nhóm. Đã clone thì `git switch main` và `git pull --ff-only origin main`,
sau khi lưu/commit công việc đang làm. [Git workflow](docs/GIT_WORKFLOW.md).

Kiểm tra khung ngay sau khi cài, chưa cần raw/workbook/API:

```bash
python run_pipeline.py --status
python -m unittest discover -s tests -v
```

Hiện `--status` liệt kê TODO, bộ test nền có 11 tests. Xem [phạm vi kiểm chứng](docs/VERIFICATION.md).

## Dataset và phạm vi nhóm

Nguồn: [Inside Airbnb Toronto](https://data.insideairbnb.com/canada/on/toronto/) (CC BY 4.0).
Mã dữ liệu **DSE2049-C01-G10-toronto**, tiền tệ **CAD**. Theo workbook được giao cho nhóm:
**2025-09-11, 2025-12-12, 2026-03-19, 2026-06-15**.
Giá chỉ phân tích ở mốc cuối. Calendar không dùng để phân tích giá; unavailable không đồng nghĩa booked.

Trang đề hiện liệt kê mốc thứ hai Toronto là `2025-11-11`, khác `2025-12-12` trong workbook
của nhóm. Config hiện theo workbook; không tự đổi ngày để khớp ví dụ trên trang.
Giữ mã/ngày đúng phân công và ghi rõ nguồn này trong báo cáo.

| Mốc | Listings | Calendar | Reviews | Neighbourhoods |
|---|---|---|---|---|
| 2025-09-11 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/visualisations/neighbourhoods.geojson) |
| 2025-12-12 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/visualisations/neighbourhoods.geojson) |
| 2026-03-19 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/visualisations/neighbourhoods.geojson) |
| 2026-06-15 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/visualisations/neighbourhoods.geojson) |

Downloader: `python scripts/download_data.py configs/toronto.yaml`.
Raw ở `data/raw/<ngày>/`; workbook giữ nguyên ở `data/assignments/assignment.xlsx`.
Cả hai thư mục đều gitignore; không commit raw/workbook/key và không mở rồi lưu lại bằng Excel.
Nếu đã tải dữ liệu, đặt đúng tên/path theo [data/README.md](data/README.md); không phải tải lại.
Chép workbook gốc vào path trên; hoặc dùng `--assignment` cho data check và sửa
`assignment.path` trong config khi chạy phân tích. Người mới phải tự chuẩn bị raw/workbook,
vì pull Git chỉ lấy file đã commit.
ID dài giữ dạng chuỗi/số nguyên chính xác, không qua float.
Vùng `analysis_area` là 8 hình chữ nhật từ workbook, không phải neighbourhood hành chính.
Danh sách cố định 1.000 listing không đo được entry/exit hay quy mô toàn thị trường Toronto.

## Luồng data check đã hoàn thành và giữ nguyên

[Hướng dẫn đầy đủ](docs/DATA_CHECK_WORKFLOW.md). Các lệnh sau tự xuất CSV/notes/diagnostics
vào `reports/checks/`; dữ liệu gốc không bị sửa.

| Người | Lệnh |
|---|---|
| Đức | `python scripts/check_data.py --part listings` |
| Hiếu | `python scripts/check_data.py --part listing-details` |
| Nam | `python scripts/check_data.py --part calendar` |
| Phan Huy | `python scripts/check_data.py --part reviews` |
| Nhóm trưởng | `python scripts/check_data.py --part merge` |

Hoặc `python scripts/check_data.py --part all` để kiểm chứng lại trước khi nộp.
Phần reviews lọc bằng **review_id**, 5.000/mốc. Câu 2 lấy trực tiếp hai cột workbook **1.000/100**.
Merge tạo `check_DSE2049-C01-G10-toronto.csv` có 16 cột và 4 dòng; có lỗi thì tạo `.draft.csv`.
Bản `report_answers.md` tự sinh là gợi ý, cần nhóm trưởng đọc trước khi nộp.
Script `scripts/check_calendar.py` và `reports/check_calendar.csv` do Nam đã đóng góp được giữ nguyên;
script/kết quả listings của Đức cũng giữ nguyên. Luồng data check chung tiếp tục dùng
`scripts/check_data.py`; đây là lệnh được hướng dẫn cho mọi máy và không cần pandas.

## Luồng phân tích để các thành viên tự làm

```bash
python run_pipeline.py --status
python -m unittest discover -s tests -v
```

`--status` liệt kê module/owner còn TODO, không đọc raw hay gọi API.
CI hiện kiểm data check và đường nối giữa module bằng test doubles; CI xanh **không có nghĩa**
thuật toán của các thành viên hoặc bài cả kỳ đã hoàn thành.

Sau khi tất cả module cần thiết đã triển khai/test/review và đặt `READY = True`:

```bash
# Phân tích, tạm bỏ LLM/evaluation/guest KPI/hình LLM:
python run_pipeline.py --config configs/toronto.yaml --skip-llm
# Nếu raw đã đủ cả CSV và GeoJSON, thêm --no-download để dùng file local:
python run_pipeline.py --config configs/toronto.yaml --skip-llm --no-download
# Khi đã đủ phần LLM và nhãn sentiment thật:
export GEMINI_API_KEY='YOUR_API_KEY'
python run_pipeline.py --config configs/toronto.yaml
```

PowerShell: `$env:GEMINI_API_KEY='YOUR_API_KEY'`. `.env.example` chỉ mô tả biến, không tự load `.env`.
Model/seed/taxonomy/paths nằm trong config. `assignment` chỉ workbook của nhóm; loader kiểm
ngày/mã/tiền tệ khớp config và lọc IDs trước khi gọi module.
LLM nhận 1.000 ID được đánh dấu; 100 dấu x nhãn tay là danh sách cần gán nhãn, chưa phải sentiment.

Pipeline đang dừng rõ nếu còn TODO. `--demo --skip-llm` cũng chưa chạy phân tích thật cho đến khi
các module được triển khai. Demo là dữ liệu giả, không dùng trong báo cáo.

Output sau khi triển khai: `data/processed/real/` chứa cleaned, baseline, LLM và kpi_*.csv;
`reports/generated/real/` chứa QA, EDA, evaluation; `figures/real/` chứa hình của từng người.
QA thật còn được xuất vào `reports/qa_report.csv`. Terminal báo trạng thái và đường dẫn;
CSV/hình là đầu ra để đối chiếu, không cần chụp terminal hoặc chép kết quả vào notebook.
[Hợp đồng hàm và bảng](docs/CONTRACTS.md).

## Quy trình đóng góp

1. Pull `main` sau khi commit/lưu công việc đang làm; tạo branch cho một task.
2. Đọc file được giao và `CONTRACTS.md`; triển khai TODO trong `src/airbnb/`.
3. Test riêng phần mình trước, kể cả khi pipeline chung còn bị chặn bởi TODO của bạn khác.
4. Bổ sung test, phần báo cáo `reports/sections/tvN.md`, tài liệu và AI_USAGE nếu có dùng AI.
5. Kiểm diff, chỉ stage file liên quan, commit bằng tài khoản mình, push branch và mở PR.
6. Reviewer kiểm logic/số liệu; nhóm trưởng merge rồi mọi người pull `main`.

Không chỉ đổi `READY` hoặc xóa comment để coi là hoàn thành. Khi giữ đúng hàm và schema,
import sẵn có tự dùng code mới; nhóm trưởng chỉ sửa luồng nếu thêm bước hoặc đổi giao diện.
Code không chạy download/API ở cấp module. [Ví dụ làm module](docs/IMPLEMENTATION_GUIDE.md)
· [Lệnh Git và xử lý conflict](docs/GIT_WORKFLOW.md).

Đầu ra phân tích tự sinh đang gitignore; ghi lệnh, số liệu chính và giới hạn trong PR/phần báo cáo.
Data check có quy ước commit CSV/notes nhỏ riêng. Ảnh có thể minh họa nhưng không thay code,
test và file kết quả. Không dùng `git add .` để gom cả file của người khác.

## Trước khi nộp bài cuối

AI tạo khung/data check được ghi trong [AI_USAGE.md](AI_USAGE.md); mỗi thành viên cập nhật khi dùng AI.
Nhóm cần chốt bên nhận phân tích, hoàn thiện QA và 5–8 KPI, hình không gian/thời gian/LLM,
baseline và đánh giá trên 100 nhãn thật. KPI theo `analysis_area` hiện chưa thay thế được
yêu cầu neighbourhood: Hiếu và nhóm trưởng phải xác minh cách xử lý cột thiếu và ghi rõ
phương án trước khi chốt bài. Cohort cố định cũng chưa đủ để suy luận entry/exit toàn thị trường.

Sau khi hoàn thành: clone sạch, chạy đầy đủ có LLM bằng khóa môi trường, tái tạo số liệu/hình,
ghép `reports/report.pdf` tối đa 10 trang và ghi mã commit. Hạn ghi trong đề là
22/11/2026, tag `final`; thao tác tag nằm trong [GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).
Data check đạt và CI xanh hiện tại chưa có nghĩa bài phân tích cuối đã hoàn thành.
