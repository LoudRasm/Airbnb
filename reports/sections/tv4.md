# Phần TV4 — Phân tích Calendar & Availability theo thời gian/vùng (Vũ Phạm Khánh Nam)

Mã dữ liệu `DSE2049-C01-G10-toronto`, tiền tệ `CAD`, 4 mốc: `2025-09-11`, `2025-12-12`, `2026-03-19`, `2026-06-15`.
Phạm vi: 1.000 listing ID của nhóm theo workbook, cả 4 mốc (365.000 dòng calendar/mốc; tổng 1.460.000 dòng trước lọc cửa sổ). Quy tắc chi tiết: [docs/CONTRACTS.md](../../docs/CONTRACTS.md) và [docs/KPI.md](../../docs/KPI.md).

## Mục tiêu và cách xử lý

Xử lý bảng `calendar.csv.gz` theo luồng streaming (`io.rows` / `loading.snapshot_rows`) để tính tỷ lệ mở lịch đặt phòng (`availability_rate`) trong cửa sổ dự báo 30 ngày và 90 ngày kể từ ngày snapshot, không nạp toàn bộ file nén vào RAM và **tuyệt đối không sử dụng cột `price` của bảng calendar**.

- **`calendar.aggregate(records, snapshot, window_days, listing_ids)`:** Lọc các bản ghi thuộc 1.000 `listing_id` của nhóm trong khoảng `[snapshot, snapshot + window_days)`, khử trùng lặp theo khóa `(snapshot_date, listing_id, date)` trước khi cộng dồn `available_days` (`available == 't'`) và `observed_days` (`available in {'t', 'f'}`). Đồng thời đếm các bất thường dữ liệu qua dictionary `issues` (`invalid_calendar_date`, `orphan_calendar`, `duplicate_calendar`, `invalid_available`).
- **`calendar.metrics(calendar, listings, cfg)`:** Kết hợp bảng `calendar` đã tổng hợp với `listings` để tính `availability_rate` có trọng số theo `observed_days` cho từng cặp `(snapshot_date, analysis_area)` (8 vùng chữ nhật của workbook).
- **`calendar.weekday_weekend_breakdown(records, snapshot, window_days, listing_ids)`:** Hàm bổ trợ phân tách tỷ lệ sẵn có giữa ngày thường (Thứ 2 – Thứ 5) và cuối tuần (Thứ 6 – Chủ nhật) trên cùng cửa sổ quan sát.
- **`viz_calendar.render(tables, figures, cfg)`:** Xuất 3 biểu đồ chuẩn (`tv4_availability_timeline_by_area.png`, `tv4_availability_by_analysis_area.png`, `tv4_price_vs_availability_latest.png`) kèm cơ chế fallback PNG chuẩn khi chạy trên môi trường CI không cài `matplotlib`.

## Lệnh chạy và file kết quả

```bash
python -m unittest discover -s tests -p test_calendar_analysis.py -v   # 6 unit test cho calendar & viz
python -m unittest discover -s tests -v                                # 59 test toàn repo
python scripts/check_calendar.py --config configs/toronto.yaml         # Data check calendar
```

| File | Nội dung |
|---|---|
| `src/airbnb/calendar.py` | Xử lý streaming `aggregate()`, tổng hợp KPI `metrics()` và phân tách `weekday_weekend_breakdown()` (`READY = True`) |
| `src/airbnb/viz_calendar.py` | Xuất 3 biểu đồ chuẩn PNG theo thời gian, vùng và tương quan giá mốc cuối (`READY = True`) |
| `tests/test_calendar_analysis.py` | 6 unit test kiểm tra streaming, cửa sổ 30/90 ngày, dedupe, đếm lỗi và biểu đồ |
| `notebooks/04_calendar.ipynb` | Notebook chạy phân tích đầy đủ trên dữ liệu thật của nhóm |
| `figures/tv4_*.png` | 4 biểu đồ trực quan hóa kết quả calendar (gitignore output tự sinh) |
| `data/processed/real/calendar_summary.csv` & `kpi_calendar.csv` | Bảng kết quả sau khi chạy pipeline chung (gitignore) |

## Số liệu chính (chạy trên raw của nhóm)

- **Chất lượng dữ liệu và độ phủ quan sát:** Cả 4 mốc đều có đủ 1.000 listing và 365.000 dòng/mốc; không phát hiện lỗi trùng khóa `(snapshot_date, listing_id, date)`, ngày sai định dạng hoặc trạng thái `available` ngoài `{t, f}` (`issues = {}`). Tuy nhiên, tổng số ngày quan sát thực tế (`observed_days`) đạt **99,78% → 98,48%** so với mức lý thuyết `90.000` ngày (`1.000 × 90`): mốc `2025-09-11` có 800 listing đủ 90 ngày và 200 listing đạt 89 ngày; mốc `2026-06-15` có 628 listing đạt 89 ngày và 372 listing đạt 88 ngày (do thời điểm thu thập thực tế `last_scraped` của Inside Airbnb trễ 1–2 ngày so với ngày danh nghĩa của snapshot).
- **Tổng hợp toàn cohort (1.000 listing) qua 4 mốc:**

| Snapshot | Cửa sổ 90d (`avail / obs`) | Availability 90d (TB trọng số) | Median 90d theo listing | Availability 30d (TB trọng số) | Hết phòng 90d (`avail = 0`) | Mở kín 90d (`100%`) | Weekday 90d (T2–T5) | Weekend 90d (T6–CN) |
|---|---|---|---|---|---|---|---|---|
| `2025-09-11` | `52.643 / 89.800` | **58,62%** | 67,60% | **42,13%** | 116 listing | 104 listing | 59,62% | 57,28% |
| `2025-12-12` | `59.507 / 89.440` | **66,53%** | 78,65% | **54,65%** | 97 listing | 179 listing | 67,12% | 65,71% |
| `2026-03-19` | `53.470 / 89.281` | **59,89%** | 63,33% | **49,06%** | 79 listing | 164 listing | 60,88% | 58,59% |
| `2026-06-15` | `45.724 / 88.628` | **51,59%** | 50,56% | **42,74%** | 84 listing | 96 listing | 52,40% | 50,58% |

- **Availability 90 ngày theo 8 vùng phân tích (`analysis_area`):**

| Vùng (`analysis_area`) | Số listing (`n`) | `2025-09-11` | `2025-12-12` | `2026-03-19` | `2026-06-15` | Biến động (Mốc 4 − Mốc 1) |
|---|---|---|---|---|---|---|
| `A01` | 130 | 62,67% | 70,42% | 61,72% | **47,73%** | **−14,94%** |
| `A02` | 130 | 52,39% | 60,97% | 53,64% | **45,85%** | −6,55% |
| `A03` | 126 | 63,70% | 70,64% | 63,00% | **55,30%** | −8,40% |
| `A04` | 121 | 60,39% | 69,11% | 61,26% | **52,54%** | −7,85% |
| `A05` | 120 | 61,09% | 65,30% | 56,71% | **57,15%** | −3,93% |
| `A06` | 121 | 51,97% | 61,56% | 53,84% | **50,25%** | −1,72% |
| `A07` | 130 | 53,92% | 62,02% | 61,58% | **50,06%** | −3,86% |
| `A08` | 122 | 63,13% | 72,38% | 67,34% | **54,53%** | −8,60% |

## Phát hiện

1. **Tính mùa vụ rõ rệt giữa mùa đông và mùa hè:** Tỷ lệ mở lịch 90 ngày đạt đỉnh vào mốc mùa đông `2025-12-12` (**66,53%**, với 179 listing mở trống toàn bộ 90 ngày) và giảm xuống đáy vào mùa cao điểm hè `2026-06-15` (**51,59%**). Xu hướng này lặp lại đồng nhất trên toàn bộ 8 vùng phân tích.
2. **Độ mở lịch ngắn hạn (30 ngày) luôn thấp hơn trung hạn (90 ngày):** Ở cả 4 mốc, `availability_rate` trong 30 ngày tới thấp hơn cửa sổ 90 ngày từ **10,8 đến 16,5 điểm phần trăm** (mốc cuối: 42,74% so với 51,59%), cho thấy lịch đặt phòng sát ngày đã được lấp đầy hoặc chủ nhà khóa lịch sớm hơn so với giai đoạn 31–90 ngày tiếp theo.
3. **Chênh lệch ngày thường và cuối tuần:** Ở tất cả các mốc, tỷ lệ phòng còn trống vào cuối tuần (Thứ 6 – Chủ nhật) luôn thấp hơn ngày thường (Thứ 2 – Thứ 5) khoảng **1,4 – 2,3 điểm phần trăm**, phản ánh nhu cầu lưu trú ngắn ngày cao hơn vào dịp cuối tuần.
4. **Phân hóa mạnh theo vùng và mối liên hệ với giá ở mốc cuối (`2026-06-15`):** `A02` (45,85%) và `A01` (47,73%) có tỷ lệ trống thấp nhất; riêng `A01` giảm mạnh nhất qua 4 mốc (**−14,94 điểm phần trăm**). Đối chiếu với giá niêm yết từ bảng `listings` tại mốc cuối (980 listing có giá), nhóm 67 listing kín lịch hoàn toàn (`available_days = 0`) có giá trung vị chỉ **111,36 CAD/đêm**, thấp hơn một nửa so với nhóm 913 listing vẫn còn ngày trống (**230,21 CAD/đêm**).

## Giới hạn

- **Availability không đồng nghĩa với Occupancy (tỷ lệ lấp đầy):** Trạng thái `available = 'f'` trong Inside Airbnb gộp chung cả ngày đã có khách đặt lẫn ngày chủ nhà chủ động khóa lịch (bảo trì, sử dụng cá nhân hoặc tạm ngừng cho thuê), nên không được suy diễn `1 - availability_rate` là công suất khai thác thực tế.
- **Độ phủ ngày quan sát phụ thuộc `last_scraped`:** Khi một listing được quét trễ 1–2 ngày sau ngày snapshot danh nghĩa, cửa sổ `[snapshot, snapshot + window_days)` sẽ khuyết 1–2 ngày đầu kỳ; việc dùng mẫu số là `observed_days` (thay vì cố định `expected_days = 90`) giúp tỷ lệ không bị bóp méo bởi độ trễ thu thập.
- **Phạm vi mẫu cố định và quy tắc không dùng giá calendar:** Kết luận chỉ áp dụng cho 1.000 listing ID của nhóm trong 8 vùng chữ nhật `analysis_area` (không phải ranh giới hành chính `neighbourhood_cleansed` và không suy rộng ra toàn Toronto). Bảng calendar không dùng để tính biến động giá theo ngày/cuối tuần; biểu đồ `tv4_price_vs_availability_latest.png` chỉ dùng giá niêm yết từ bảng `listings` tại mốc cuối `2026-06-15`.