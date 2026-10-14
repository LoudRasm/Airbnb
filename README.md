# Nhóm 10 Inside Airbnb Toronto

Bài tập lớn Lập trình xử lý dữ liệu, lớp **UET.DSE2049 1**, nhóm **10**, học kỳ 1 năm 2026–2027.
[GitHub nhóm](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10)
· [Đề bài](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html)

**Repo có hai phần khác nhau:**

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
mỗi người một mốc. Mỗi người viết test và report section riêng. [Phân công](docs/TEAM.md).

## Cài môi trường và cập nhật code

Python đã kiểm thử: **3.13.7**, xem `.python-version`. Khung dùng Python stdlib;
không cần pandas để chạy data check. Nếu thêm thư viện cho phần mình, ghim `==` trong requirements.

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

## Dataset và phạm vi nhóm

Nguồn: [Inside Airbnb Toronto](https://data.insideairbnb.com/canada/on/toronto/) (CC BY 4.0).
Mã dữ liệu **DSE2049-C01-G10-toronto**, tiền tệ **CAD**. Theo workbook mới:
**2025-09-11, 2025-12-12, 2026-03-19, 2026-06-15**.
Giá chỉ phân tích ở mốc cuối. Calendar không dùng để phân tích giá; unavailable không đồng nghĩa booked.

| Mốc | Listings | Calendar | Reviews | Neighbourhoods |
|---|---|---|---|---|
| 2025-09-11 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2025-09-11/visualisations/neighbourhoods.geojson) |
| 2025-12-12 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2025-12-12/visualisations/neighbourhoods.geojson) |
| 2026-03-19 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2026-03-19/visualisations/neighbourhoods.geojson) |
| 2026-06-15 | [listings.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/listings.csv.gz) | [calendar.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/calendar.csv.gz) | [reviews.csv.gz](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/reviews.csv.gz) | [neighbourhoods.geojson](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/visualisations/neighbourhoods.geojson) |

Downloader: `python scripts/download_data.py configs/toronto.yaml`.
Raw ở `data/raw/<ngày>/`; workbook giữ nguyên ở `data/assignments/assignment.xlsx`.
Cả hai thư mục đều gitignore; không commit raw/workbook/key và không mở rồi lưu lại bằng Excel.
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
luồng data check chung tiếp tục dùng `scripts/check_data.py`.

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
QA thật còn được xuất vào `reports/qa_report.csv`. [Hợp đồng hàm và bảng](docs/CONTRACTS.md).

## Quy trình đóng góp

Tạo branch, triển khai TODO của mình, thêm test/tài liệu và mở PR. Không chỉ đổi `READY` hoặc
xóa comment để coi là hoàn thành. Nhóm trưởng review và tích hợp qua import sau merge;
thành viên tự commit công việc bằng tài khoản mình. Code không chạy download/API ở cấp module.
Chi tiết và ví dụ import: [IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md).
AI tạo khung/data check được ghi trong [AI_USAGE.md](AI_USAGE.md); mỗi thành viên cập nhật khi dùng AI.
Trước bài cuối: đủ QA/KPI/hình/LLM được kiểm chứng, nhãn thật, report PDF tối đa 10 trang,
clean clone chạy đầy đủ bằng key khác rồi mới tag `final` theo đề.
