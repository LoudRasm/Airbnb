# Phạm vi kiểm chứng

Cập nhật **2026-11-22**. Baseline trước sửa: main `86b609e`.
Môi trường kiểm tra: Python **3.13.7**, dependencies theo `requirements.txt`; `pip check` không có xung đột.
Không gọi Gemini thật. Không sửa raw, workbook, 100 nhãn tay hoặc phiếu gán nhãn.

## Kiểm thử phần mềm

```bash
python -m pytest -q
python scripts/label_reviews.py check
python run_pipeline.py --status
```

**139 tests đạt** trong bản sao chỉ chứa các file bàn giao, dùng môi trường cài mới từ `requirements.txt`.
Có 14 cảnh báo deprecation của thư viện vẽ. Có kiểm tra đúng đường dẫn KPI `data/processed/kpi_*.csv`.

Bộ test gồm unittest của các thành viên và test dạng hàm của Hiếu; CI chạy pytest để thu đủ.
Có test tích hợp chạy các thuật toán/vẽ thật trên fixture nhỏ, cache giả chỉ trong thư mục tạm:
không key/không mạng, cache miss dù có key, đổi text không dùng nhầm cache, full → skip giữ kết quả,
render lỗi không xuất một nửa, chuyển raw path và thêm mốc thứ năm bằng config, đổi config về một mốc
không để lại hình giá cũ. Có test cho listing thiếu calendar, tỷ lệ chưa xác định, nhóm giá rỗng,
supply neighbourhood đủ listing thiếu giá, nhãn đúng đường dẫn config, ngày ISO và thứ tự mốc.

Fixture/cache giả chỉ xác nhận hành vi phần mềm, không phải kết quả Gemini hoặc chất lượng mô hình thật.
READY biểu thị code tích hợp và kiểm thử; không ghi thay tên reviewer hay xác nhận peer review của ai.

## Chạy trên dữ liệu thật

Đã chạy luồng không LLM bằng source hiện tại, workbook/raw cục bộ, bật chặn mạng trong lần kiểm cô lập:

```bash
python run_pipeline.py --config configs/toronto.yaml --skip-llm --no-download
```

Đầu ra: data/processed/real/non_llm, reports/generated/real/non_llm, figures/real/non_llm.
Lần chạy cô lập đầu mất khoảng 46 giây; thời gian phụ thuộc máy và cache font.

| Bảng | Số dòng |
|---|---:|
| Listings sau QA | 4.000 |
| Calendar summary (cửa sổ 90 ngày) | 4.000 |
| Reviews sau khử trùng giữa mốc | 5.000 |
| Market KPI (8 vùng × 4 mốc) | 32 |
| Calendar KPI | 32 |
| Neighbourhood KPI (125 × 4 mốc) | 500 |
| Missingness toàn bộ cột nguồn | 344 |
| KPI impact | 20 |
| Cohort / chuyển tiếp mốc | 4 / 3 |
| Hình không LLM | 11 |

QA report có schema_drift, cross_host_id_changed, cross_category_changed, cross_coordinates_moved
và neighbourhood_not_in_reference. Listings vẫn đủ 1.000/mốc; giá cuối có 980/1.000 hợp lệ,
supply neighbourhood cuối **1.000**, không còn bị giảm xuống 980 do lọc giá. Giá phân tích mốc trước để trống;
missingness giá nguồn vẫn là 69/1.000/28/20 theo bốn mốc để đối chiếu báo cáo đầu vào.
Calendar thiếu **200/560/719/1.372 listing-ngày trong cửa sổ 90 ngày**; mẫu số expected là 90.000/mốc.
Điều này khác số dòng calendar thô 365.000/mốc; không coi là dữ liệu thô bị giảm sau khi sửa.
Host-ID changes vẫn 3/35/37, room-type changes 0/0/0 như phần phân tích cohort đã có.

## Đối chiếu báo cáo đầu vào

Chạy nguyên data_check.py vào thư mục kiểm riêng, không ghi đè reports/checks lịch sử.
CSV tổng hợp ban đầu khớp cả **4 dòng × 16 cột**; SHA256 raw, bytes, số dòng, số cột,
đếm missing, room type, no-review và mẫu 1.000/100 đều khớp. Số cột thiếu ≥90%: 2/6/12/12.
ID đọc dạng chuỗi; reviews lọc theo review_id độc lập listing_id.

Hai bảng thành phần calendar_summary và listing_details có **workbook fingerprint lịch sử khác**,
chỉ khác cột metadata đó; không tự sửa để qua merge. Nếu nộp data check mới, chạy lại hai phần bằng cùng
workbook hiện tại. Workbook hiện tại và báo cáo listings/reviews/merge_status dùng SHA256
`08cf3abf4fd13693c3ebca169e0190ee6866e75c2b262f432c39081978b3a351`.
Biên bản [data_alignment_2026-11-16.json](../reports/data_alignment_2026-11-16.json) ghi chênh lệch và hash nhãn tay.

## Chạy đầy đủ từ cache Gemini

Bốn mốc giữ theo workbook, gồm `2025-12-12` đã được giảng viên xác nhận với nhóm trưởng.
Ngày 2026-11-22, bản sao chỉ chứa các file bàn giao tải đủ 16 tệp và chạy hết lệnh mặc định mà không có workbook cục bộ hoặc khóa Gemini. SHA-256 của 16 tệp tải lại khớp dữ liệu đã dùng trong nhóm.
Chạy lại lệnh với các phiên bản cài mới từ `requirements.txt` xác nhận đủ sáu CSV KPI ở `data/processed/kpi_*.csv`.
Đầu ra thật có 4.000 listings, 5.000 review duy nhất và 1.000 dự đoán Gemini.
Trên cùng 100 nhãn tay, Gemini đạt 96% accuracy và 0,8594 macro-F1. Baseline đạt 95% và 0,8278.
Đối chiếu trong `reports/generated/real/evaluation.csv` và [PDF chính](../reports/Nhom10_InsideAirbnb_Report.pdf).
