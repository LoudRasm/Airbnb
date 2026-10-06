# BÀI TẬP LỚN INSIDE AIRBNB – TORONTO

## PHẦN 1. HIỂU BÀI TOÁN VÀ ĐỊNH HƯỚNG THỰC HIỆN

### 1.1. Mục tiêu của bài tập lớn

Nhóm đóng vai một **đội phân tích dữ liệu Airbnb**, lựa chọn một bên liên quan cụ thể và xây dựng một quy trình phân tích dữ liệu hoàn chỉnh cho thành phố Toronto.

Bài toán không chỉ yêu cầu phân tích dữ liệu bằng notebook mà yêu cầu xây dựng một **data pipeline có khả năng chạy lại tự động**, từ tải dữ liệu, kiểm tra chất lượng, xử lý dữ liệu, tính KPI, phân tích review bằng LLM đến trực quan hóa và tạo các kết quả phục vụ báo cáo.

Pipeline cuối cùng phải có khả năng chạy bằng một lệnh và hoạt động kể cả khi giảng viên thay một snapshot Toronto khác vào file cấu hình. Vì vậy các mốc thời gian, đường dẫn dữ liệu và tham số không được hard-code trong source code.

---

### 1.2. Stakeholder được lựa chọn

Nhóm định hướng phân tích cho:

**Toronto Short-Term Rental & Tourism Market Monitoring Team**

Có thể hiểu là một nhóm phân tích phục vụ cơ quan quản lý du lịch/thị trường lưu trú Toronto.

Câu hỏi tổng quát:

> **Thị trường Airbnb tại Toronto thay đổi như thế nào theo thời gian và khu vực về nguồn cung, mức giá, khả năng sẵn có, cấu trúc host và trải nghiệm của khách hàng?**
>

Từ đó bài phân tích tập trung vào ba góc nhìn:

**Spatial:** Airbnb phân bố ở đâu và neighbourhood nào nổi bật?

**Temporal:** Thị trường thay đổi thế nào giữa các snapshot?

**Guest experience:** Khách hàng đang hài lòng hoặc phàn nàn về điều gì?

---

### 1.3. Các snapshot bắt buộc

Toronto phải sử dụng bốn snapshot:

- 2025-09-11
- 2025-11-11
- 2026-03-19
- 2026-06-15

---

### 1.4. Các nguồn dữ liệu cần xử lý

Mỗi snapshot gồm bốn nguồn chính.

#### A. `listings.csv.gz`

Đây là bảng trung tâm mô tả các Airbnb listing.

Các nhóm thông tin chính:

- Listing ID
- Host ID
- Giá
- Room type
- Property type
- Sức chứa
- Minimum nights
- Availability
- Review scores
- Latitude/longitude
- Neighbourhood
- Thông tin host

Đơn vị phân tích:

> Một listing tại một snapshot.
>

Khóa logic:

`(snapshot_date, listing_id)`

Không được coi cùng một listing xuất hiện ở nhiều snapshot là duplicate.

---

#### B. `calendar.csv.gz`

Chứa trạng thái theo từng ngày của từng listing:

- listing_id
- calendar date
- available
- price
- minimum nights
- maximum nights

Đây dự kiến là bảng lớn nhất.

Khóa logic:

`(snapshot_date, listing_id, calendar_date)`

Calendar được dùng chủ yếu để phân tích:

- availability 30/90 ngày;
- giá tương lai;
- weekday/weekend pricing;
- thay đổi availability và pricing giữa các snapshot.

Không nên coi `unavailable = booked`, vì host có thể chủ động block ngày. Vì vậy nhóm sẽ sử dụng thuật ngữ **availability/unavailability proxy**, không gọi trực tiếp là occupancy.

---

#### C. `reviews.csv.gz`

Chứa review dạng văn bản:

- review_id
- listing_id
- review date
- reviewer
- comments

Đây là input cho phần LLM.

Các snapshot sau có thể chứa lại những review cũ, do đó cần deduplicate review trước khi phân tích.

Khóa chính ưu tiên:

`review_id`

---

#### D. `neighbourhoods.geojson`

Chứa ranh giới địa lý của các neighbourhood Toronto.

Dùng để xây dựng:

- choropleth map;
- listing density;
- median price theo neighbourhood;
- guest experience theo neighbourhood.

Đề bài yêu cầu sử dụng listings, calendar, reviews và neighbourhood boundaries trong pipeline phân tích.

---

## 1.5. Sản phẩm cuối cùng cần tạo ra

Pipeline tổng quát:

**Raw Data**

↓

**Data QA**

↓

**Cleaned / Processed Data**

↓

**KPI**

↓

**LLM Review Analysis**

↓

**Visualization**

↓

**Technical Report**

Pipeline cần chạy bằng dạng:

`python run_pipeline.py --config configs/toronto.yaml`

Repo cuối cùng cần có tối thiểu:

- `configs/`
- `data/raw/`
- `data/processed/`
- `data/samples/`
- `src/`
- `figures/`
- `reports/`
- `run_pipeline.py`
- `.python-version`
- `.env.example`
- `.gitignore`
- `AI_USAGE.md`
- `README.md`
- `requirements.txt`

Đây cũng gần với cấu trúc repo chính thức được đề bài khuyến nghị.

---

## 1.6. Chiến lược xử lý dữ liệu

Không xử lý bốn snapshot thành bốn project riêng.

Thay vào đó:

**4 snapshots → 1 common processing pipeline**

Mọi hàm phải có khả năng nhận snapshot bất kỳ.

Ví dụ:

`load_snapshot(date)`

thay vì:

`load_sep_data()`

`load_nov_data()`

Điều này giúp pipeline tổng quát và chạy được với snapshot mới khi giảng viên kiểm thử.

---

## 1.7. Data model dự kiến

### Listings table

Khóa:

`snapshot_date + listing_id`

### Calendar table

Khóa:

`snapshot_date + listing_id + calendar_date`

### Reviews table

Khóa:

`review_id`

### Neighbourhood table

Khóa:

`neighbourhood`

Sau bước preprocessing, các bảng sẽ được liên kết thông qua:

`listing_id`

và:

`neighbourhood_cleansed`

---

## 1.8. Data Quality Assurance

Đề bài yêu cầu QA phải xử lý tối thiểu:

- missing values;
- outliers;
- duplicates;
- incorrect types;
- category drift;
- duplicate/collision giữa các snapshot.

Mỗi QA rule phải có:

**Name → Condition → Reason → Action**

và kết quả phải được ghi vào:

`reports/qa_report.csv`

bao gồm số dòng chịu tác động và ảnh hưởng lên KPI trước/sau QA.

Nhóm dự kiến xây khoảng **15–20 QA rules**.

Các nhóm QA chính:

1. Schema validation.
2. Missing critical values.
3. Duplicate validation.
4. Referential integrity.
5. Data type validation.
6. Price outliers.
7. Minimum-night anomalies.
8. Geographical anomalies.
9. Review-date anomalies.
10. Calendar-date anomalies.
11. Category drift.
12. Schema drift giữa snapshot.

Nguyên tắc:

> Ưu tiên flag dữ liệu bất thường trước khi tự động xóa.
>

---

## 1.9. Bộ KPI dự kiến

Đề yêu cầu 5–8 KPI, phải có KPI theo thời gian, theo neighbourhood và ít nhất một KPI sử dụng kết quả LLM.

Nhóm dự kiến sử dụng 7 KPI:

### KPI 1 – Observed Listing Supply

Số listing đang xuất hiện tại mỗi snapshot.

Mục tiêu: đo quy mô thị trường.

---

### KPI 2 – Median Nightly Price

Median giá listing.

Breakdown:

- snapshot;
- neighbourhood;
- room type.

Mục tiêu: đánh giá mức giá và sự khác biệt không gian.

---

### KPI 3 – Entire-home Share

Tỷ lệ listing thuộc loại entire home/apartment.

Mục tiêu: mô tả cấu trúc nguồn cung.

---

### KPI 4 – Multi-listing Host Share

Tỷ lệ listing thuộc host sở hữu/vận hành nhiều listing.

Mục tiêu: đánh giá mức độ chuyên nghiệp hóa của thị trường.

---

### KPI 5 – 90-day Availability Rate

Tỷ lệ ngày còn available trong 90 ngày tiếp theo.

Mục tiêu: đánh giá trạng thái nguồn cung ngắn hạn.

---

### KPI 6 – Listing Entry/Exit Rate

Giữa hai snapshot:

- New listing;
- Retained listing;
- Disappeared listing.

Mục tiêu: đánh giá mức độ biến động/churn của thị trường.

---

### KPI 7 – Guest Experience Issue Rate

Dựa trên kết quả LLM:

- % negative/mixed review;
- hoặc % review đề cập tiêu cực tới cleanliness/noise/value/etc.

Mục tiêu: đo trải nghiệm của khách hàng.

---

## 1.10. Phân tích LLM

LLM sẽ được dùng để biến review dạng text thành dữ liệu có cấu trúc.

Mỗi review trả về:

- sentiment: positive/mixed/negative;
- positive aspects;
- negative aspects;
- language.

Aspect taxonomy dự kiến:

- location;
- cleanliness;
- host;
- value;
- amenities;
- noise;
- safety;
- check-in.

Nhóm sử dụng một taxonomy cố định để các review có thể aggregate thành KPI.

---

### Baseline không dùng LLM

Đề bài yêu cầu so sánh LLM với một phương pháp không dùng LLM và ít nhất 100 review được gán nhãn tay.

Baseline có thể gồm:

- sentiment: VADER/rule-based sentiment;
- language: language detection;
- aspect: keyword matching.

---

### Ground truth

Dự kiến label thủ công:

**200 reviews**

Chia đều:

**40 reviews/người × 5 người**

Kết quả cuối cùng đánh giá:

- Accuracy;
- Macro-F1;
- LLM vs baseline;
- error analysis.

---

## 1.11. Visualization dự kiến

Không tập trung làm quá nhiều biểu đồ EDA.

Mục tiêu là khoảng **6–8 hình chính**, mỗi hình phục vụ một câu hỏi.

Dự kiến:

1. Listing supply qua bốn snapshot.
2. Median price qua bốn snapshot.
3. Median price map theo neighbourhood.
4. Entry/exit listing giữa các snapshot.
5. Price vs availability theo neighbourhood.
6. Guest sentiment.
7. Negative review aspects.
8. Guest-experience map.

Storytelling:

**How large is the market?**

↓

**Where is it concentrated?**

↓

**How has it changed?**

↓

**How are listings priced and made available?**

↓

**What do guests think?**

↓

**Which areas require attention?**

---

# PHẦN 2. LỘ TRÌNH THỰC HIỆN

Deadline cuối:

**23:59, Chủ nhật 22/11/2026.**

Mục tiêu là hoàn thành phần kỹ thuật trước deadline khoảng một tuần để có thời gian test và chuẩn bị vấn đáp.

---

## GIAI ĐOẠN 1 – Setup & Data Understanding

### 05/10 – 11/10

Mục tiêu:

Hiểu dữ liệu và tạo nền tảng chung cho cả nhóm.

Công việc:

- tạo/finalize GitHub repo;
- dựng cấu trúc thư mục;
- tạo `toronto.yaml`;
- tạo `.gitignore`;
- tạo `.python-version`;
- tạo `requirements.txt`;
- viết script download;
- tải thử bốn snapshot;
- khảo sát schema;
- kiểm tra kích thước từng dataset;
- thống nhất stakeholder;
- thống nhất research questions;
- thống nhất KPI.

Đầu ra:

- repo chuẩn;
- config Toronto;
- downloader chạy được;
- raw data đúng cấu trúc;
- data dictionary bản đầu;
- tài liệu mô tả KPI.

**Milestone nội bộ 1:** pipeline tải được cả bốn snapshot.

---

## GIAI ĐOẠN 2 – QA & Preprocessing

### 12/10 – 18/10

Mục tiêu:

Xây dựng tầng dữ liệu sạch chung cho toàn nhóm.

Công việc:

- xây QA framework;
- xác định primary/composite keys;
- xử lý data type;
- parse price;
- xử lý missing;
- xác định outlier;
- duplicate detection;
- category drift;
- schema drift;
- xử lý review duplicate;
- kiểm tra referential integrity;
- chuẩn hóa output.

Đầu ra:

- `qa.py`;
- processed listings;
- processed calendar;
- processed reviews;
- `qa_report.csv`;
- data dictionary hoàn chỉnh.

**Milestone nội bộ 2:** mọi thành viên sử dụng cùng processed dataset.

---

## GIAI ĐOẠN 3 – Core Analysis

### 19/10 – 25/10

Ba hướng chạy song song.

### Listings

Phân tích:

- supply;
- price;
- room type;
- host;
- neighbourhood;
- churn.

### Calendar

Phân tích:

- availability 30/90 ngày;
- future pricing;
- weekday/weekend;
- temporal behaviour.

### Reviews

Chuẩn bị:

- deduplicate reviews;
- sampling;
- thiết kế annotation guideline;
- baseline.

Đầu ra:

- các bảng KPI phiên bản đầu;
- các bảng aggregate phục vụ visualization;
- review sample để label.

**Milestone nội bộ 3:** hoàn thành các KPI không dùng LLM.

---

## GIAI ĐOẠN 4 – LLM & Evaluation

### 26/10 – 01/11

Mục tiêu:

Hoàn thành phần bắt buộc liên quan tới LLM.

Công việc:

- chốt prompt;
- structured JSON output;
- API integration;
- caching;
- retry/error handling;
- chạy baseline;
- mỗi thành viên label 40 reviews;
- tạo 200 ground-truth labels;
- chạy LLM;
- tính Accuracy;
- tính Macro-F1;
- error analysis;
- estimate cost.

Đầu ra:

- `llm.py`;
- `baseline.py`;
- `evaluate.py`;
- manual labels;
- LLM processed result;
- evaluation table.

**Milestone nội bộ 4:** LLM chạy end-to-end và được đánh giá.

---

## GIAI ĐOẠN 5 – KPI Integration & Visualization

### 02/11 – 08/11

Mục tiêu:

Tích hợp toàn bộ phân tích thành một câu chuyện thống nhất.

Công việc:

- finalize 7 KPI;
- tạo `kpi_*.csv`;
- spatial analysis;
- temporal analysis;
- LLM KPI;
- tạo 6–8 final figures;
- chỉnh title;
- axis;
- legend;
- annotation;
- currency;
- captions.

Đầu ra:

- toàn bộ KPI CSV;
- toàn bộ figures;
- insight cho từng figure.

**Milestone nội bộ 5:** không còn phân tích lớn nào chưa hoàn thành.

---

## GIAI ĐOẠN 6 – Report & Integration

### 09/11 – 15/11

Mục tiêu:

Ghép project thành sản phẩm hoàn chỉnh.

Công việc:

- viết technical report;
- thống nhất terminology;
- kiểm tra KPI giữa code/report;
- hoàn thiện README;
- hoàn thiện AI_USAGE;
- hoàn thiện requirements;
- hoàn thiện pipeline;
- loại hard-code;
- kiểm tra paths.

Report có thể chia:

1. Introduction & stakeholder.
2. Data.
3. Pipeline.
4. QA.
5. KPI & analysis.
6. LLM methodology.
7. Results.
8. Limitations.
9. Conclusion.

**Milestone nội bộ 6:** có bản release candidate hoàn chỉnh.

---

## GIAI ĐOẠN 7 – Testing & Viva Preparation

### 16/11 – 19/11

Không thêm feature mới trừ khi thực sự cần.

Test:

1. Clone repo sang thư mục mới.
2. Tạo Python environment mới.
3. Cài từ requirements.
4. Đặt API key mới.
5. Chạy một lệnh.
6. Kiểm tra toàn bộ output.
7. Thử thêm một Toronto snapshot ngoài bốn snapshot chính.
8. Kiểm tra deterministic sampling.
9. Kiểm tra `-skip-llm` nếu triển khai.

Quan trọng nhất:

**Random snapshot test**

Vì giảng viên có thể đổi snapshot trong config rồi chạy pipeline.

---

## GIAI ĐOẠN 8 – Final Freeze

### 20/11 – 22/11

Chỉ:

- sửa bug;
- kiểm tra số liệu;
- kiểm tra citations;
- kiểm tra README;
- kiểm tra AI_USAGE;
- proofread report;
- final clean clone;
- tag release.

Sau khi xác nhận:

`git tag final`

`git push origin final`

---

# PHẦN 3. PHÂN CÔNG CÔNG VIỆC CHO 5 THÀNH VIÊN

## Nguyên tắc phân công

Không chia:

- người 1 làm Sep;
- người 2 làm Nov;
- người 3 làm Mar;
- người 4 làm Jun.

Cách này tạo bốn pipeline khác nhau và khó đảm bảo consistency.

Thay vào đó:

> **Mỗi thành viên sở hữu một module xuyên suốt cả bốn snapshot.**
>

Mỗi người đều phải có:

- coding;
- data processing;
- analysis;
- visualization hoặc reporting;
- responsibility rõ ràng.

---

# THÀNH VIÊN 1

## Pipeline Architecture & Market Dynamics

### Coding

Phụ trách:

- `configs/toronto.yaml`;
- config loader;
- `download.py`;
- `run_pipeline.py`;
- orchestration giữa các module;
- logging;
- integration.

### Data analysis

Phụ trách:

- total listings;
- new listings;
- retained listings;
- disappeared listings;
- listing entry rate;
- listing exit rate;
- cross-snapshot market evolution.

### Visualization

Phụ trách:

- listing supply timeline;
- entry/exit/churn visualization.

### Report

Viết:

- Problem definition;
- stakeholder;
- overall pipeline;
- market evolution.

### Management

Ngoài technical work:

- quản lý GitHub issues;
- theo dõi deadline;
- merge PR;
- đảm bảo interface giữa các module thống nhất;
- tổ chức code review;
- integration cuối.

### Deliverables

- `configs/toronto.yaml`
- `src/download.py`
- `run_pipeline.py`
- supply/churn KPI
- market-evolution figures

---

# THÀNH VIÊN 2 – DATA QA & PREPROCESSING

### Coding

Phụ trách:

- `qa.py`;
- common cleaning utilities;
- type conversion;
- schema checking;
- QA rule framework.

### QA rules

Bao gồm:

- missing;
- duplicate;
- wrong type;
- invalid date;
- price anomaly;
- minimum-night anomaly;
- category drift;
- schema drift;
- referential integrity;
- cross-snapshot duplication.

### Data analysis

Phân tích:

- mức độ missing;
- outlier rate;
- category changes;
- schema changes;
- ảnh hưởng QA lên KPI.

### Documentation

Phụ trách:

- data dictionary;
- QA rule documentation;
- `qa_report.csv`.

### Visualization

Có thể làm:

- QA summary;
- missingness/drift visualization nếu cần cho report.

### Report

Viết:

- Data description;
- Data quality;
- Cleaning methodology;
- Limitations liên quan tới dữ liệu.

### Deliverables

- `src/qa.py`
- processed schema
- `reports/qa_report.csv`
- data dictionary

---

# THÀNH VIÊN 3 – LISTINGS, HOST & SPATIAL ANALYSIS

### Coding

Phụ trách processing liên quan tới:

- listings;
- hosts;
- neighbourhood;
- GeoJSON.

### Analysis

Phân tích:

- nightly price;
- price distribution;
- room type;
- property type;
- entire-home share;
- host structure;
- multi-listing hosts;
- neighbourhood structure.

### KPI

Owner:

**Median Nightly Price**

**Entire-home Share**

**Multi-listing Host Share**

### Spatial analysis

Phụ trách:

- merge GeoJSON;
- neighbourhood aggregation;
- spatial KPI.

### Visualization

Phụ trách:

- Toronto price map;
- listing-density map;
- room-type distribution;
- host concentration.

### Report

Viết:

- Spatial market structure;
- Listing characteristics;
- Host characteristics.

### Deliverables

- listings processing functions
- spatial aggregation
- listings KPI
- maps
- spatial-analysis section

---

# THÀNH VIÊN 4 – CALENDAR & TEMPORAL ANALYSIS

### Coding

Phụ trách xử lý dataset calendar lớn.

Ưu tiên:

- Polars lazy processing;
- aggregation trước khi giữ data trong RAM;
- efficient output.

### Analysis

Phân tích:

- availability 30 ngày;
- availability 90 ngày;
- weekday/weekend pricing;
- future pricing;
- calendar changes giữa snapshots.

### KPI

Owner:

**90-day Availability Rate**

Có thể bổ sung supporting metrics:

- weekend price premium;
- 30-day availability;
- future median price.

### Visualization

Phụ trách:

- availability timeline;
- weekday/weekend comparison;
- calendar heatmap;
- price-availability scatter.

### Report

Viết:

- Calendar methodology;
- Availability analysis;
- Temporal market patterns.

### Deliverables

- calendar processing functions
- availability KPI
- temporal tables
- temporal figures

---

# THÀNH VIÊN 5 – REVIEWS, NLP & LLM

### Coding

Phụ trách:

- review preprocessing;
- review deduplication;
- sampling;
- Gemini/API integration;
- JSON parsing;
- caching;
- retry handling;
- baseline;
- evaluation.

### LLM task

Trích xuất:

- sentiment;
- positive aspects;
- negative aspects;
- language.

### Baseline

Phụ trách:

- non-LLM sentiment;
- keyword aspect detection;
- language detection.

### Evaluation

Tính:

- Accuracy;
- Macro-F1;
- error analysis;
- estimated full-dataset cost.

### KPI

Owner:

**Guest Experience Issue Rate**

### Visualization

Phụ trách:

- sentiment distribution;
- sentiment over time;
- negative aspects;
- LLM vs baseline performance.

### Report

Viết:

- LLM methodology;
- baseline;
- evaluation;
- guest-experience insights;
- cost estimation.

### Deliverables

- `src/llm.py`
- `src/baseline.py`
- `src/evaluate.py`
- LLM results
- evaluation table
- LLM figures

---

# 3.1. Công việc chung bắt buộc cho cả 5 người

Một số phần không nên giao cho một người duy nhất.

## Manual labeling

200 reviews:

- TV1: 40
- TV2: 40
- TV3: 40
- TV4: 40
- TV5: 40

TV5 tổng hợp nhưng không chịu toàn bộ workload.

---

## Code review

Không tự merge code của mình.

Gợi ý reviewer:

- TV1 review TV3
- TV2 review TV5
- TV3 review TV2
- TV4 review TV1
- TV5 review TV4

Có thể thay đổi vòng reviewer theo từng sprint.

---

## Report

Người làm analysis nào phải tự viết section tương ứng.

Không giao toàn bộ report cho leader.

Leader chỉ:

- thống nhất structure;
- chỉnh consistency;
- ghép final version.

---

## Viva preparation

Tuần cuối:

### Session 1

TV1 giải thích pipeline cho cả nhóm.

### Session 2

TV2 giải thích QA.

### Session 3

TV3 giải thích spatial/listings.

### Session 4

TV4 giải thích calendar.

### Session 5

TV5 giải thích LLM.

Sau đó random hỏi chéo.

Điều này cần thiết vì đề quy định mọi thành viên phải giải thích được toàn bộ code, số liệu và quyết định của nhóm chứ không chỉ phần mình làm.

---

# 3.2. Bảng phân công tổng hợp

| Thành viên | Module chính | KPI chính | Visualization | Report |
| --- | --- | --- | --- | --- |
| TV1  | Pipeline + Integration | Supply + Churn | Market evolution | Intro + Pipeline + Evolution |
| TV2 | QA + Preprocessing | QA impact | QA/Drift | Data + QA + Limitations |
| TV3 | Listings + Spatial | Price + Entire-home + Host | Maps + Listing structure | Spatial analysis |
| TV4 | Calendar + Temporal | Availability | Temporal + Calendar | Calendar analysis |
| TV5 | Reviews + LLM | Guest Experience | Sentiment + Aspect | LLM analysis |

---

# 3.3. Đánh giá workload tương đối

| Thành viên | Coding | Analysis | Visualization | Documentation/Management |
| --- | --- | --- | --- | --- |
| TV1 | 4/5 | 3/5 | 2/5 | 4/5 |
| TV2 | 4/5 | 3/5 | 2/5 | 4/5 |
| TV3 | 3/5 | 4/5 | 4/5 | 2/5 |
| TV4 | 4/5 | 4/5 | 3/5 | 2/5 |
| TV5 | 4/5 | 4/5 | 3/5 | 2/5 |

Workload tương đối cân bằng.

TV1 và TV2 có nhiều trách nhiệm integration/documentation.

TV3–TV5 có workload phân tích và visualization nặng hơn.

---

# 3.4. Dependency giữa các thành viên

Không triển khai tuần tự hoàn toàn.

Sau khi TV1 hoàn thành downloader và schema contract:

**TV2 – QA**

**TV3 – Listings**

**TV4 – Calendar**

**TV5 – Reviews**

có thể làm song song.

Luồng tổng quát:

`TV1: Config + Download`

↓

`Common raw data`

↓

`TV2: QA/Preprocessing`

↙ ↓ ↘

`TV3 Listings | TV4 Calendar | TV5 Reviews`

↓

`KPI + Figures`

↓

`TV1 Integration`

↓

`Final Pipeline`

---

# 3.5. Quy tắc Definition of Done

Một task chỉ được coi là hoàn thành khi:

- chạy được cho cả bốn snapshot;
- không hard-code snapshot trong source code;
- có input/output rõ ràng;
- xử lý lỗi cơ bản;
- code được push lên branch;
- có commit message rõ ràng;
- ít nhất một người khác review;
- output được lưu đúng folder;
- số liệu kiểm tra hợp lý;
- người viết code giải thích được logic;
- người review cũng hiểu phần code đó.

---

# 3.6. Mục tiêu cuối cùng của nhóm

Project nên được đóng gói bằng một câu:

> **Build a reproducible data pipeline to monitor how Toronto's short-term rental market evolves across neighbourhoods and time, combining listing, calendar, spatial and guest-review data with validated LLM-based guest-experience analysis.**
>

Scope cuối cùng:

- **4 required Toronto snapshots**
- **1 reproducible pipeline**
- **15–20 QA rules**
- **7 main KPIs**
- **200 manually labelled reviews**
- **LLM + non-LLM baseline**
- **6–8 final visualizations**
- **1 technical report ≤10 pages**
- **5 technical workstreams có workload tương đối cân bằng**

Ưu tiên lớn nhất của nhóm không phải bổ sung thật nhiều feature, mà là làm chắc bốn yếu tố:

**Reproducibility**

**Data Quality**

**Meaningful Spatial/Temporal Analysis**

**Validated LLM Analysis**

Đây là các yếu tố bám sát nhất vào yêu cầu chính thức của bài tập lớn.
