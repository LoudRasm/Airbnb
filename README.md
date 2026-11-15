# Nhóm 10 Inside Airbnb Toronto

Bài tập lớn Lập trình xử lý dữ liệu, lớp **UET.DSE2049 1**, nhóm **10**, học kỳ 1 năm 2026–2027.
[GitHub nhóm](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10)
· [Đề bài](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html)

## Việc cần làm ngay — cập nhật 15/11/2026

- **Cả 5 người:** đọc [hướng dẫn gán nhãn tay](docs/MANUAL_LABELING.md), mở phiếu của mình
  trong [data/samples/labeling/](data/samples/labeling/README.md), tự đọc và gán 20 review.
  Phiếu đã có sẵn text đúng ID; chưa có nhãn cảm xúc. Không cần raw/workbook/API để làm phần này.
- **Code/phần báo cáo:** làm theo [checklist từng người](docs/FINAL_CHECKLIST.md):
  [Bạn — TV1](docs/checklists/tv1.md), [Đức](docs/checklists/tv2.md),
  [Hiếu](docs/checklists/tv3.md), [Nam](docs/checklists/tv4.md), [Phan Huy](docs/checklists/tv5.md).
- **Bàn giao:** mỗi người sửa phần mình trên branch, test và mở PR; nhóm trưởng review/merge.
  TV5 ghép 100 nhãn qua PR; TV1 tích hợp và finalize sau khi các phần đã hoàn thiện.

**Phần riêng TV1 đã triển khai:** coverage cohort, thay đổi host_id/room_type, hai SVG,
14 tests và [báo cáo cá nhân](reports/sections/tv1.md). Chạy độc lập, không cần module của bạn khác:

```bash
python scripts/run_tv1.py --config configs/toronto.yaml
python scripts/run_tv1.py --demo
python -m unittest discover -s tests -p test_tv1.py -v
```

CSV: `data/processed/real/tv1/`; hình: `figures/real/tv1/`; metadata/tóm tắt:
`reports/generated/real/tv1/`. Mặc định chỉ chiếu ID/host/room từ raw đã lọc workbook, chưa thay
cho QA chung. Khi bảng sạch có sẵn, thêm `--listings data/processed/real/listings.csv` để chạy
trên cleaned. Demo là dữ liệu giả. Không tải/gọi API hoặc sửa code của owner khác.
analysis/viz_market có `IMPLEMENTED=True`, READY giữ False chờ Nam review theo quy trình;
status sẽ ghi REVIEW cho hai module này khi import calendar đã được sửa.
20 nhãn tay TV1 vẫn cần bạn tự đọc/chốt. Các bước finalize chung chưa đánh dấu hoàn thành.

**Blocker đang có, chưa sửa thay owner:** calendar.py sót nội dung merge nên `--status` và
integration đang lỗi import/cú pháp; Nam tự xử lý theo checklist. Đức đã có QA/EDA và 42 test
QA đạt, còn hình/kiểm chứng tích hợp; nhiều module của các bạn khác vẫn TODO.
Các lệnh phân tích dưới đây là luồng mục tiêu, chưa phải toàn pipeline đang chạy được.

Ví dụ Đức kiểm phiếu riêng, chạy độc lập với lỗi calendar:

```bash
python scripts/label_reviews.py check --member tv2
```

Đổi tv2 thành tv1/tv3/tv4/tv5. Check báo còn trống/ca khó là đúng khi chưa gán xong; không tự
điền nhãn để vượt kiểm tra. Mỗi người chỉ commit phiếu mình, không cùng sửa CSV nhãn cuối.

## Trạng thái hiện tại

Repo giữ cấu trúc **module trong `src/airbnb/`**. Đây là source chung: mỗi thành viên sửa
file được giao trên branch riêng, mở PR vào `main`; sau merge, pipeline import code mới.
Không cần folder theo tên người hoặc chép code sang một bộ source khác.

**Repo có hai phần:**

| Phần | Trạng thái | Lệnh |
|---|---|---|
| Kiểm tra dữ liệu đầu vào theo workbook | Đã chạy trên dữ liệu thật; giữ nguyên | `python scripts/check_data.py --part ...` |
| QA, EDA, KPI, LLM và hình cho bài cả kỳ | Đã có QA/EDA của Đức; các phần khác đang phát triển/TODO, calendar đang chặn import | `python run_pipeline.py --status` sau khi Nam sửa lỗi |

Khung ban đầu có chữ ký hàm, hướng dẫn đầu vào/đầu ra và `TODO[TV1]` đến `TODO[TV5]` để
thành viên tự triển khai. Các module chưa xong tiếp tục giữ `READY = False`/`NotImplementedError`;
có code không đồng nghĩa đã được kiểm chứng. Trạng thái mới nhất xem checklist ngày 15/11.
Implementation AI cũ nằm trong lịch sử và AI_USAGE; không dùng làm đóng góp cá nhân giả.
[Hướng dẫn triển khai và import](docs/IMPLEMENTATION_GUIDE.md).

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
| Bắt đầu gán 20 review và bàn giao 100 nhãn thật | [MANUAL_LABELING.md](docs/MANUAL_LABELING.md) |
| Sửa lỗi đúng owner, PR/merge rồi nhóm trưởng finalize | [FINAL_CHECKLIST.md](docs/FINAL_CHECKLIST.md) |

Sơ đồ trong đề gợi ý tên module bên trong `src/`; repo đặt chúng trong package `airbnb`
để import ổn định. Những thư mục và file bàn giao ở gốc vẫn giữ theo đề.

### Các file `viz_*` là gì? Bản final có giữ không?

`viz` là viết tắt của visualization (trực quan hóa). Đề gợi ý `viz.py` và yêu cầu có hình
theo góc độ không gian, thời gian và LLM. Các tên `viz_calendar.py`, `viz_spatial.py`… là
cách nhóm chia code theo phần việc, không phải tên file bắt buộc hay yêu cầu phân tích thêm.

| File trong src/airbnb/ | Vai trò | Người phụ trách |
|---|---|---|
| `viz.py` | Gọi các hàm vẽ và gom đường dẫn hình; không viết chung mọi biểu đồ vào đây | Nhóm trưởng |
| `viz_market.py` | Hình tổng hợp cho câu hỏi phân tích chung | Nhóm trưởng |
| `viz_qa.py` | Hình về dữ liệu thiếu và chất lượng dữ liệu | Đức |
| `viz_spatial.py` | Bản đồ, so sánh theo vùng; ghi rõ giới hạn neighbourhood | Hiếu |
| `viz_calendar.py` | Hình availability/coverage theo thời gian; không phân tích giá calendar | Nam |
| `viz_reviews.py` | Hình cảm xúc/khía cạnh từ kết quả LLM | Phan Huy |

```text
run_pipeline.py
    → tính các bảng dữ liệu và KPI
    → viz.render_all(...)
        → viz_market / viz_qa / viz_spatial / viz_calendar / viz_reviews
        → lưu hình vào figures/real/ (hoặc figures/demo/ khi chạy demo)
```

Mỗi người triển khai `render(tables, figures, cfg)` trong file vẽ của mình: nhận các bảng đã
xử lý, lưu hình vào thư mục `figures` được truyền vào và trả `list[Path]`. Dùng tên hình riêng
để tránh ghi đè; không tự tải raw/gọi LLM lại trong bước vẽ. `--skip-llm` bỏ `viz_reviews`.
`viz_market.py` đã sinh hình TV1; các file vẽ còn lại vẫn TODO. Có tên file không có nghĩa đã sinh được hình.

**Bản final giữ các module mà chương trình sử dụng**, kể cả các file `viz_*` không được liệt
kê riêng trong sơ đồ đề. Các file hiện đã được `viz.py` import và gọi; không xóa chỉ để tên
file giống sơ đồ minh họa. Nếu nhóm gộp/đổi module sau này, phải sửa import/lời gọi và kiểm
tra lại pipeline. Hình nộp phải sinh tự động từ luồng chung, dùng số liệu khớp báo cáo;
notebook khám phá và ảnh terminal không thay bước này.

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

Kiểm tra không cần raw/workbook/API. Hiện test QA/nhãn chạy độc lập; status/toàn bộ suite
sẽ còn lỗi calendar cho tới khi Nam sửa:

```bash
python run_pipeline.py --status
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p test_qa.py -v
python -m unittest discover -s tests -p test_manual_labels.py -v
```

Khi import thông, `--status` liệt kê từng module/owner và READY/TODO.
Không dùng kết quả 11 tests của starter cũ làm trạng thái hiện tại.
Xem [phạm vi kiểm chứng](docs/VERIFICATION.md) và checklist mới.

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
Phiếu đã chia sẵn 20/người; TV5 chạy `python scripts/label_reviews.py merge` chỉ khi đủ nhãn
và đã giải quyết ca khó. Nhóm trưởng duyệt CSV cuối qua PR, không chạy lệnh này để tạo nhãn tự động.

Hiện pipeline chưa import được vì calendar. Sau khi Nam sửa, guard tiếp tục dừng nếu còn TODO.
`--demo --skip-llm` cũng cần các module được triển khai. Demo là dữ liệu giả, không dùng trong báo cáo.

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
yêu cầu neighbourhood: Hiếu và nhóm trưởng xác minh cột/coverage thực tế từng mốc, đối chiếu
GeoJSON và ghi rõ phương án. Không mặc định cột thiếu theo ghi chú starter cũ.
Cohort cố định cũng chưa đủ để suy luận entry/exit toàn thị trường.

Sau khi hoàn thành: clone sạch, chạy đầy đủ có LLM bằng khóa môi trường, tái tạo số liệu/hình,
ghép `reports/report.pdf` tối đa 10 trang và ghi mã commit. Hạn ghi trong đề là
22/11/2026, tag `final`; thao tác tag nằm trong [GIT_WORKFLOW.md](docs/GIT_WORKFLOW.md).
Data check đạt và CI xanh hiện tại chưa có nghĩa bài phân tích cuối đã hoàn thành.
