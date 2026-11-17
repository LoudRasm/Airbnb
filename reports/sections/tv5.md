# Phần TV5 — Phân tích Reviews, Baseline, LLM & Trải nghiệm khách hàng (Phan Ngọc Huy)

Mã dữ liệu: `DSE2049-C01-G10-toronto` · 4 mốc: `2025-09-11`, `2025-12-12`, `2026-03-19`, `2026-06-15`.
Phạm vi theo workbook: **5.000 review ID** được giao toàn nhóm, trong đó **1.000 review ID** thuộc tập mẫu LLM (`Review / Mẫu LLM = x`) và **100 review ID** thuộc tập gán nhãn thủ công (`Review / Nhãn tay = x`, chia 5 gói × 20 review cho TV1–TV5).

## 1. Phương pháp luận & Kiến trúc Module

Toàn bộ phần việc của TV5 được chuẩn hóa trong 6 module tại `src/airbnb/` theo đúng giao ước `docs/CONTRACTS.md` và `docs/checklists/tv5.md`:

| Module | Hàm chính | Chức năng & Ràng buộc kỹ thuật |
|---|---|---|
| `src/airbnb/reviews.py` | `collect(records, snapshot, existing)` | Lọc theo `review_id` (giữ chuỗi chữ số ASCII chính xác, không lọc thêm theo `listing_id`); kiểm ngày ISO, comment rỗng/chỉ chứa HTML `<br/>`; khử trùng lặp giữa các mốc (`first_seen_snapshot`) và phát hiện xung đột văn bản (`review_text_collision`) để luôn giữ văn bản khớp mốc cuối `2026-06-15`. Kèm các hàm tiền xử lý `clean_comment`, `detect_language_simple`, `extract_aspect_keywords`. |
| `src/airbnb/baseline.py` | `predict(review)`, `predict_with_aspects(review)` | Phân loại cảm xúc không dùng LLM (`keyword_baseline`) dựa trên từ điển đa ngữ (`en`, `fr`, `es`, `de`), cửa sổ phủ định (`not`, `never`, `didn't`), liên từ đối lập (`but`, `except`, `however`, `only`) và mẫu sự cố nhỏ đã giải quyết (`small problem ... helped us immediately`). Không gán mặc định một nhãn cố định. |
| `src/airbnb/llm.py` | `validate(obj, aspects)`, `analyze(reviews, cfg, root, review_ids)`, `estimate_cost(...)` | Tích hợp Gemini (`gemini-3.5-flash-lite`) với `responseMimeType: application/json`, kiểm tra nghiêm ngặt `sentiment` $\in \{\text{positive}, \text{mixed}, \text{negative}\}$ và các khía cạnh thuộc đúng 8 nhóm trong `configs/toronto.yaml`. Lưu cache JSONL kèm provenance (`review_id`, `text_sha256`, `model`, `prompt_sha256`, `aspects`), tự động vô hiệu hóa cache cũ nếu đổi prompt/model/taxonomy/text, retry khi lỗi mạng/timeout và không bao giờ biến lỗi API thành nhãn mặc định. |
| `src/airbnb/evaluate.py` | `evaluate(predictions, labels, source)`, `evaluate_detailed(...)` | Đối chiếu dự đoán của LLM và Baseline trên cùng tập `review_id` gán nhãn tay; kiểm tra tính duy nhất của `review_id` và báo lỗi `ValueError` ngay nếu thiếu bất kỳ dự đoán nào (không âm thầm thu nhỏ mẫu đánh giá). Xuất `paired_n`, `manual_n`, `accuracy`, `macro_f1`, `meets_100_paired`. |
| `src/airbnb/review_kpi.py` | `guest_kpi(predictions, listings, cfg)` | Tính **KPI 7 — Guest Experience Issue Rate** $= \frac{N_{\text{mixed}} + N_{\text{negative}}}{N_{\text{sample}}}$, tỷ lệ từng nhãn cảm xúc, tỷ lệ khen/chê theo 8 khía cạnh và tỷ lệ theo `analysis_area` khi ghép `listing_id` (khử trùng lặp `listing_id` giữa 4 snapshot để không nhân bội số review). |
| `src/airbnb/viz_reviews.py` | `render(tables, figures, cfg)` | Sinh 4 biểu đồ SVG chuẩn (`tv5_sentiment_distribution.svg`, `tv5_negative_aspects.svg`, `tv5_sentiment_over_time.svg`, `tv5_model_comparison.svg`) ghi rõ phạm vi mẫu và kích thước mẫu `n`. |

## 2. Gán nhãn thủ công (Manual Labeling)

- Đã hoàn thành gán nhãn thủ công cho đủ **20/20 review** thuộc gói `data/samples/labeling/tv5.json` theo đúng hướng dẫn `docs/MANUAL_LABELING.md`, điền đầy đủ `sentiment`, `needs_review = false` và `note` tiếng Việt giải thích căn cứ gán nhãn, giữ nguyên tuyệt đối các trường gốc (`review_id`, `listing_id`, `date`, `comments`, `text_sha256`).
- Kiểm tra bằng công cụ chuẩn của nhóm:
  ```bash
  .\.venv\Scripts\python.exe scripts/label_reviews.py check --member tv5
  # Kết quả: Checked 20 reviews; unresolved checks: 0 (exit code 0)
  ```
- Phân bố 20 nhãn tay của TV5:
  - `positive`: **17/20** (85,0%) — bao gồm cả trường hợp có sự cố nhỏ lúc check-in nhưng host xử lý ngay (`review_id = 1464576983883991511`).
  - `mixed`: **2/20** (10,0%) — khen chỗ ở chung nhưng phàn nàn rõ về ga trải giường có vết bẩn/bồn rửa rỉ nước (`1470433948828735644`) hoặc bếp xuống cấp (`1503006261195439072`).
  - `negative`: **1/20** (5,0%) — mở đầu xã giao `"ok" house` nhưng toàn bộ nội dung phàn nàn nhà cũ thiếu bảo trì, tóc và cốc nhựa bẩn, cầu thang trơn nguy hiểm (`1454434461842749610`).
- Khi cả 5 thành viên (TV1–TV5) hoàn tất gói nhãn cá nhân (`unresolved checks: 0` cho cả 100 review), chạy lệnh `python scripts/label_reviews.py merge` để xuất `data/samples/manual_labels.csv` (`paired_n = 100`, `meets_100_paired = True`).

## 3. Lệnh chạy độc lập & Kiểm thử

```bash
.\.venv\Scripts\python.exe scripts/label_reviews.py check --member tv5
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_tv5.py" -v
.\.venv\Scripts\python.exe scripts/run_tv5.py --config configs/toronto.yaml --demo
.\.venv\Scripts\python.exe scripts/run_tv5.py --config configs/toronto.yaml
# Khi có GEMINI_API_KEY và chạy full LLM:
.\.venv\Scripts\python.exe scripts/run_tv5.py --config configs/toronto.yaml --with-llm
```

- **10/10 unit tests trong `tests/test_tv5.py` đạt 100%**, kiểm tra toàn diện: deduplication & phát hiện collision văn bản giữa các mốc, giữ nguyên ID 19 chữ số, phân loại baseline (`positive`, `mixed`, `negative`), `llm.validate`, `llm.analyze` (mock API, cache hit/miss khi đổi text/model/taxonomy, retry và xử lý lỗi), `evaluate` (bắt lỗi thiếu dự đoán/trùng ID, tính Macro-F1), `review_kpi` (không nhân bản review theo snapshot) và `viz_reviews.render`.

## 4. Kết quả Đánh giá, KPI 7 & Ước tính Chi phí API

### 4.1. Hiệu năng LLM và Baseline trên toàn bộ 100 nhãn tay (`n = 100`)
- Kết quả đối chuẩn thực tế trên toàn bộ 100 review gán nhãn thủ công (`reports/generated/real/tv5/evaluation.csv`):
  - **LLM (`gemini-3.5-flash-lite`):**
    - **Accuracy:** `96,0%` (`96/100` review khớp hoàn toàn nhãn tay).
    - **Macro-F1:** `0,8594` (`85,94%`), đáp ứng xuất sắc yêu cầu phân loại trên tập dữ liệu mất cân bằng.
  - **Keyword Baseline:**
    - **Accuracy:** `95,0%` (`95/100` review khớp nhãn tay).
    - **Macro-F1:** `0,8278` (`82,78%`).
  - Phân tích lỗi: Baseline bắt đúng các mẫu khen rõ ràng, mẫu `negative` (`1454434461842749610`) và mẫu `mixed` có từ khóa `stain`/`drips` (`1470433948828735644`), nhưng dễ nhạy cảm với mệnh đề nhượng bộ hoặc từ vựng mô tả gián tiếp (`kitchen is bit worn out`). Đây chính là ưu thế của LLM (`gemini-3.5-flash-lite`) khi hiểu ngữ cảnh toàn câu và đa ngôn ngữ.

### 4.2. Thống kê KPI 7 (Guest Experience Issue Rate) & Khía cạnh (`data/processed/real/tv5/kpi_guest.csv`, `n = 1.000`)
- **KPI 7 — Guest Experience Issue Rate (`mixed + negative`):** `6,4%` (`64/1.000` review ghi nhận vấn đề trải nghiệm, gồm `5,0%` `mixed` và `1,4%` `negative`; `93,6%` `positive`).
- **Các khía cạnh được khen nhiều nhất (`positive_aspects`):**
  1. `host` (`75,0%`) — chủ nhà thân thiện, phản hồi nhanh, hỗ trợ nhiệt tình.
  2. `location` (`73,6%`) — gần tàu điện ngầm (subway/streetcar), trung tâm Downtown, tiện đi bộ.
  3. `amenities` (`66,3%`) và `cleanliness` (`44,5%`) — phòng sạch sẽ, tiện nghi đầy đủ.
- **Các khía cạnh bị phàn nàn nhiều nhất (`negative_aspects`):**
  1. `amenities` (`5,7%`) — thiết bị bếp cũ kỹ, bồn rửa mặt nhỏ/rò nước, điều hòa/sưởi hoặc nội thất xuống cấp.
  2. `noise` (`3,5%`) — tiếng ồn giao thông đường lớn hoặc cách âm giữa các phòng.
  3. `cleanliness` (`2,2%`) — vết bẩn trên ga giường, tóc/rác còn sót lại trong phòng tắm, mùi ẩm.
  4. `check-in` (`1,8%`), `host` (`0,9%`), `value` (`0,8%`), `safety` (`0,5%`), `location` (`0,3%`).

### 4.3. Ước tính Token & Chi phí Gemini API (`gemini-3.5-flash-lite`)
Mô hình `gemini-3.5-flash-lite` được chọn để vận hành toàn bộ pipeline nhờ nằm trong **Free Tier** của Google AI Studio (miễn phí sử dụng hoàn toàn khi tuân thủ hạn mức RPM/RPD).

Nếu tính theo đơn giá thương mại chuẩn ngoài hạn mức (\$0,30 / 1M input tokens; \$2,50 / 1M output tokens) dựa trên độ dài thực tế của review sau làm sạch (`~273,3` ký tự/review, `~394,1` input tokens/review, `~45,0` output tokens/review):

| Phạm vi chạy | Số lượng review (`n`) | Tổng Input Tokens ước tính | Tổng Output Tokens ước tính | Chi phí AI Studio Free Tier | Chi phí Pay-as-you-go tham khảo |
|---|---:|---:|---:|:---:|---:|
| Mẫu LLM theo workbook (`sample_size`) | 1.000 | ~394.082 | ~45.000 | **\$0,00 (Free)** | **\$0,2307** (~23,1 cents) |
| Toàn bộ tập review được giao (`assigned_reviews`) | 5.000 | ~1.970.412 | ~225.000 | **\$0,00 (Free)** | **\$1,1536** (~$1,15) |

Cơ chế lưu cache JSONL (`data/processed/llm_cache.jsonl`) kèm SHA-256 provenance giúp chi phí chạy lại pipeline bằng **\$0,00** cho mọi review không thay đổi nội dung.

## 5. Phối hợp & Review Code cho TV4 (`src/airbnb/calendar.py` & `src/airbnb/viz_calendar.py`)

Theo phân công chéo của nhóm (TV5 review TV4 — Vũ Phạm Khánh Nam), kết quả rà soát module `src/airbnb/calendar.py` trên nhánh `main` hiện tại như sau:

1. **Lỗi cú pháp chặn import toàn pipeline (`Blocker`):**
   - Tại [calendar.py](file:///d:/UET/DSE/Baitaplon/2627-LTXLDL-Airbnb-dse2049_1-nhom10/src/airbnb/calendar.py#L11) và [calendar.py](file:///d:/UET/DSE/Baitaplon/2627-LTXLDL-Airbnb-dse2049_1-nhom10/src/airbnb/calendar.py#L114), còn sót hai dòng nhãn nhánh khi resolve merge conflict (`feat/tv4-calendar-analysis` ở dòng 11 và `main` ở dòng 114), gây `IndentationError` ngay khi `run_pipeline.py` hoặc `tests/test_pipeline.py` import `airbnb.calendar`.
2. **Thiếu câu lệnh import ở đầu file (`Blocker`):**
   - Hàm `aggregate` sử dụng `date`, `timedelta` và `Counter` nhưng đầu file `src/airbnb/calendar.py` chưa có `from collections import Counter` và `from datetime import date, timedelta` (sẽ gây `NameError` khi gọi hàm).
3. **Vi phạm quy ước không phân tích giá calendar (`Contract Warning`):**
   - Hàm `calculate_weekend_pricing_premium` (dòng 43–95) đang đọc cột `price` từ `calendar.csv.gz`. Theo `docs/CONTRACTS.md`, `docs/checklists/tv4.md` và báo cáo kiểm tra dữ liệu (`reports/checks/report_answers.md` mục 4), cột `price` trong `calendar.csv.gz` rỗng 100% ở cả 4 mốc và nhóm thống nhất **không phân tích giá từ calendar**; đồng thời docstring/TODO cũ ở dòng 97–104 đang nằm bên dưới `return summary` của hàm này.
4. **Chưa triển khai `calendar.metrics` và `viz_calendar.render`:**
   - Hàm `metrics(calendar, listings, cfg)` tại `src/airbnb/calendar.py` và `render(tables, figures, cfg)` tại `src/airbnb/viz_calendar.py` hiện vẫn đang `raise NotImplementedError`. Đề nghị TV4 xóa dòng conflict marker, bổ sung import, hoàn thiện `metrics` (gồm cửa sổ 30/90/365 ngày theo `analysis_area` kèm denominator/coverage) và thêm `tests/test_tv4.py` trước khi bật `READY = True`.
