# AI usage

## Công cụ đã dùng (vào việc gì)
- OpenAI Codex: tạo starter repository từ tài liệu ZIP và đề bài, ngày 06/10/2026.
- Gemini API: starter cũ từng có adapter AI; hiện `llm.py` là TODO của TV5.
  Chưa chạy API và chưa có kết quả LLM thật được kiểm chứng trong khung hiện tại.

## Prompt then chốt
1. Yêu cầu tạo bộ khung repository nhóm 5 người, bốn snapshot Toronto, pipeline và Git workflow (run_pipeline.py, src/, docs/).
Nhóm bổ sung 5–10 prompt thực tế trong quá trình làm; không tạo prompt giả.

## AI sai ở đâu
Ví dụ đã xác minh ngày 14/10/2026: docs/ROADMAP.md còn yêu cầu weekend pricing từ calendar
và 200 nhãn tay; docs/DATA_CHECK_WORKFLOW.md nói script calendar bị xóa và pipeline chưa lọc
workbook. Những mô tả này không khớp yêu cầu dữ liệu/source hiện tại. Đã bỏ phân tích giá
calendar, dùng 100 review được đánh dấu và sửa mô tả script/loader. Các ví dụ tiếp theo cần
ghi lỗi thực tế, cách kiểm chứng và commit; không tạo ví dụ giả.

## Nhóm kiểm chứng thế nào
Starter có kiểm thử trên fixture giả. Nhóm phải kiểm chứng dữ liệu thật, giá trị KPI,
LLM, nhãn tay và giải thích toàn bộ code trước khi nộp. Không dùng số liệu demo trong báo cáo.

## Cập nhật 06/10/2026 — README nhóm 10
- Codex đối chiếu source local, bản phân công Markdown và đề bài; cập nhật README với
  remote GitHub nhóm, 16 URL dữ liệu, bảng owner/module và trạng thái phần còn thiếu.
- Bổ sung lại các dotfile setup/Git/CI đang thiếu trong bản repo Desktop.
- Prompt: kiểm tra chia code theo phân công, dùng code chung trên main/pull và viết README
  đúng nhóm, đường dẫn GitHub/dataset đầy đủ.

## Cập nhật 14/10/2026 — luồng xuất kết quả và tổng hợp
- Codex tạo script kiểm tra chung theo workbook, bốn phần cho TV2–TV5 và lệnh merge của TV1.
- Tích hợp lại phần calendar của Nam: đọc đúng path, bỏ phụ thuộc pandas/NumPy và ID hard-code,
  xuất CSV/notes, báo lỗi ngày mà không dừng các mốc còn lại. Lịch sử script gốc còn trong Git.
- Prompt: tạo luồng chạy kiểm tra → file kết quả → push lên repo để mọi người làm theo.
- Kiểm chứng: test ID dài, lọc review_id độc lập listing_id, đủ bốn mốc, lỗi ngày,
  thiếu dữ liệu, kết quả cũ/khác workbook và chặn merge khi chưa đủ phần.
- Chạy lại kiểm tra trên raw Toronto local; không gọi API LLM, không sửa file gốc hoặc workbook.

## Cập nhật 14/10/2026 — khung TODO theo phân công
- Theo yêu cầu nhóm trưởng, Codex bỏ implementation AI trong các module phân tích cả kỳ,
  giữ interface, TODO theo TV1–TV5, owner và trạng thái READY=False để thành viên tự làm.
- Giữ nguyên data check đã kiểm chứng, script/CSV calendar do Nam merge ở PR #1
  và script/kết quả listings của Đức ở PR #2/#3.
- TV1 có loader/orchestration và import các module; mỗi owner tự triển khai logic, test và report section.
- Prompt: giữ data check, để TODO theo phân công, sau này ghép code thành viên qua import.
- Kiểm chứng: 11 tests cho data check và integration bằng test doubles; chưa có algorithm/LLM thật trong khung TODO.
- Implementation AI cũ vẫn ở lịch sử Git; không đổi tác giả commit hoặc coi khung này là code do thành viên tự viết.

## Cập nhật 14/10/2026 — hướng dẫn module và Git workflow

- Prompt: giữ hướng module hiện tại, làm sạch README/hướng dẫn đầy đủ và commit lên Git.
- Codex chỉnh tài liệu phân công, triển khai, kết quả bàn giao, branch/PR/merge/pull và mẫu PR.
- Giữ source, TODO/READY, data check và script/kết quả đã merge của thành viên.
- Sửa tài liệu cũ mâu thuẫn; ghi rõ ngày theo workbook, giới hạn KPI neighbourhood/cohort
  và việc chạy trên mốc ngoài workbook chưa được xác minh.
- Kiểm chứng: rà đường dẫn/lệnh/interface trong tài liệu; chạy bộ 11 tests và lệnh --status.
  Không tải lại raw, không chạy lại API hoặc biến module TODO thành thuật toán đã hoàn thành.

## Cập nhật 15/10/2026 — giải thích các file vẽ trong README

- Prompt: kiểm tra đã ghi đầy đủ note hướng dẫn trong README sau khi giải thích các file viz.
- Codex bổ sung ý nghĩa viz, bảng file/người phụ trách, luồng render và đường dẫn hình,
  chữ ký hàm, trạng thái TODO và quy tắc giữ module được sử dụng trong bản final.
- Kiểm chứng: đối chiếu với `src/airbnb/viz.py` và chữ ký các module vẽ; kiểm diff tài liệu.
  Không sửa source hoặc chạy lại thuật toán/API cho thay đổi tài liệu này.

## Cập nhật 15/11/2026 — nhãn tay và checklist hoàn thiện

- Prompt: dựa vào status mới, viết hướng dẫn gán nhãn thủ công và checklist từng người;
  chưa sửa lỗi cá nhân, thành viên tự hoàn thiện/PR rồi nhóm trưởng finalize.
- Codex đối chiếu main 0df65f5, xác nhận 42 test QA đạt và calendar đang lỗi import/cú pháp.
- Bổ sung guideline, checklist TV1–TV5, liên kết README và công cụ chuẩn bị/kiểm/ghép nhãn
  độc lập pipeline. Không sửa source, cờ READY, thuật toán hay test cá nhân của thành viên.
- Trích đúng 100 ID Nhãn tay từ workbook, text raw mốc 2026-06-15, chia 20/người; mọi sentiment
  khởi tạo rỗng. AI không gán nhãn các review thật. Workbook/raw chỉ được đọc; CSV nhãn cuối còn header.
- Test công cụ dùng review/nhãn tổng hợp giả để kiểm ID dài, scope, text/nguồn thay đổi,
  nhãn trống/sai/ca khó, từ chối ghi đè và ghép đủ 100 dòng; không gọi API LLM.
- Kết quả: 9 tests nhãn, 42 QA và 6 data check đạt; full discovery có 1 lỗi tải test_pipeline
  do calendar của Nam (5 case integration chưa chạy). Không sửa/tắt test hoặc CI để che lỗi.

## Cập nhật 15/11/2026 — hoàn thiện phần code riêng TV1

- Prompt: hoàn thành nốt phần của nhóm trưởng, không liên quan phần của thành viên khác.
- Codex triển khai analysis.cohort_summary/churn và viz_market, giữ tên API legacy nhưng
  giới hạn ở hiện diện/thay đổi thuộc tính cohort; không coi ID mới/mất là market entry/exit.
- Thêm runner TV1 độc lập không import module cá nhân khác, SVG bằng stdlib, tests và báo cáo;
  nối thêm bảng/fields TV1 vào pipeline do TV1 sở hữu. Test double QA trong test_pipeline của
  TV1 được chỉnh giữ một dòng/ID đúng contract, không thay implementation QA của Đức.
- Bên nhận phân tích giả định giữ theo kế hoạch gốc, ghi vào config. Đọc raw đúng ID để kiểm
  chứng riêng; không chạy thuật toán/calendar/LLM của người khác, không đổi raw/workbook.
- Kết quả thực đo: 1.000 listing mỗi mốc; host khác nhau 930/930/937/930; host_id đổi
  3/35/37 trên 1.000 cặp, room_type đổi 0/0/0. Không giả làm kết quả toàn pipeline sau QA.
- Kiểm chứng: 14 tests TV1 đạt; toàn discovery 71 đạt/1 lỗi import calendar có sẵn. Bốn case
  orchestration đạt khi dùng calendar giả tạm; status với source calendar thật vẫn lỗi.
  Hai SVG thật đã được render và xem bố cục. Không sửa source/test/READY của thành viên khác.
- IMPLEMENTED=True nhưng READY=False chờ peer review theo workflow; 20 nhãn tay TV1 giữ
  trống để con người đọc/chốt, không dùng AI tạo gold labels hoặc ký thay reviewer.
- Status TV1 phân biệt REVIEW với TODO khi import chung chạy được; guard vẫn chặn module
  chưa READY. Test guard dùng trạng thái chưa READY tường minh để không phụ thuộc tiến độ thật của nhóm.

## Cập nhật 15/11/2026 — hoàn thiện phần TV5 (Phan Ngọc Huy)

- Prompt: hoàn thành gói nhãn cá nhân `tv5.json`, triển khai các module TV5 (`reviews.py`,
  `baseline.py`, `llm.py`, `evaluate.py`, `review_kpi.py`, `viz_reviews.py`), script chạy độc lập
  `scripts/run_tv5.py`, bộ kiểm thử `tests/test_tv5.py`, báo cáo `reports/sections/tv5.md` và review code cho TV4.
- Triển khai:
  - `reviews.collect` khử trùng lặp theo `review_id`, giữ nguyên ID chữ số dài, phát hiện xung đột
    văn bản giữa các mốc (`review_text_collision`) và đảm bảo văn bản khớp mốc cuối `2026-06-15`.
  - `baseline.predict` và `predict_with_aspects` phân loại đa ngữ theo mệnh đề, phủ định và liên từ đối lập.
  - `llm.validate`, `llm.analyze` và `llm.estimate_cost` kiểm tra chặt schema/taxonomy 8 khía cạnh,
    cache JSONL kèm SHA-256 provenance (`review_id`, `text_sha256`, `model`, `prompt_sha256`),
    retry lỗi mạng/timeout và không biến lỗi API thành nhãn mặc định.
  - `evaluate.evaluate` tính Accuracy/Macro-F1 và chặn thiếu dự đoán hoặc trùng ID.
  - `review_kpi.guest_kpi` tính KPI 7 (`guest_issue_rate`) và tỷ lệ khía cạnh/khu vực không nhân bội theo snapshot.
  - `viz_reviews.render` sinh 4 biểu đồ SVG chuẩn ghi rõ phạm vi mẫu và `n`.
- Kiểm chứng: `python scripts/label_reviews.py check --member tv5` đạt 0 lỗi; 10/10 unit tests
  trong `tests/test_tv5.py` đạt.
## Cập nhật 2026/11/17 — sửa sau rà soát và chuẩn hóa pipeline

- Yêu cầu: sửa lỗi đã rà soát, dọn phần trùng, cập nhật theo đề mới, kiểm dữ liệu trước/sau và đẩy main;
  giữ nguyên nhãn tay cùng phần code đúng của các thành viên.
- Codex dùng thuật toán đã có của từng owner, sửa điểm nối QA đầy đủ, market/neighbourhood theo mốc,
  denominator calendar, guest join và output riêng từng chế độ. Tách runner/schema/reader nhãn;
  bỏ path/ID ghi cứng trong script cũ và bản sao dictionary/catalog, CSV fallback cá nhân của notebook.
- Chuyển mặc định sang cache-only để chấm không API key; thêm lệnh tạo/kiểm cache riêng và hướng dẫn.
  Người dùng xác nhận chưa có cache thật, nên không tạo dự đoán hoặc nhãn giả để hoàn thành bài.
- Thêm/sửa test cho hợp đồng đã thay đổi, chạy dữ liệu thật không LLM và đối chiếu CSV/raw SHA256
  với data check ban đầu; xem docs/VERIFICATION.md và reports/data_alignment_2026-11-16.json.
- 100 nhãn tay/phiếu được giữ nguyên từng byte; AI không gán lại nhãn. Các cache giả dùng trong test
  chỉ nằm ở thư mục tạm. Không gọi Gemini thật, không chỉnh tác giả commit cũ, không tag final.

## Cập nhật 2026/11/17 — báo cáo và tài liệu bổ sung từ kết quả thật

- Yêu cầu: hoàn thiện báo cáo có sẵn theo cấu trúc kết luận → bằng chứng → giới hạn, giữ kiểu trình bày,
  dùng số liệu/hình thật, mỗi thành viên 20%, để MSSV tự điền; chuyển code/bảng dài sang supplement.
- Viết lại báo cáo LaTeX, sinh hình từ CSV/GeoJSON, dùng cùng số đo cho bảng/hình; thêm script tái tạo,
  supplement và source để chỉnh sửa. Giữ phần bàn giao cá nhân trong reports/sections làm lịch sử.
- Sửa nhận định cũ: calendar hai mốc cuối có coverage 99,20%/98,48%; Gemini 96% accuracy nhưng recall mixed 3/7;
  120 review có negative aspect khác KPI 64 mixed/negative. Không gọi model “xuất sắc” từ accuracy tổng thể.
- Đếm 679.139 review duy nhất ở raw toàn thành phố mốc cuối cho ước tính chi phí; không gọi 5.000 review được giao là toàn Toronto.
  Ước tính ký tự/token không gồm thinking token và không phải hóa đơn.
- Các PDF được render và kiểm tra từng trang; số liệu được đối chiếu lại với CSV, ma trận nhầm lẫn và mã băm nguồn.

## Cập nhật 21/10/2026 — TV2: QA & preprocessing listings

- Công cụ: Claude. Dùng hỗ trợ viết `src/airbnb/qa.py`, `eda.py`, `tests/test_qa.py`, `scripts/run_qa.py`; đọc `docs/`, đề bài, PDF kế hoạch và workbook để bám contract.
- Prompt chính: (1) bắt đầu triển khai `qa.clean_listings` theo CONTRACTS/QA.md; (2) chạy QA trên 4 file listings thật và lọc đúng
  1.000 ID của nhóm; (3) hoàn thiện `qa.py`
- AI sai ở đâu (đã phát hiện):
  1. `median_price_before` trong QA report tính sau khi giá đã bị sửa tại chỗ nên sai; test `test_price_outlier_nulled_and_median_changes` bắt được, đã sửa bằng cách tính median trước khi áp rule.
  2. AI nói chưa có workbook dù file đã nằm trong project; sau đó mở workbook và lọc đúng ID nhóm 10.
  3. AI thêm tham số thứ 4 vào `clean_listings`, trái quy định "không đổi chữ ký âm thầm" của CONTRACTS; đã bỏ, rule tham chiếu geojson chuyển thành hàm riêng `check_neighbourhood_reference`.
  4. Một số kỳ vọng trong test do AI tính sai (median của 100, 200, 90000, 90000 là 45.100 chứ không phải 145; tỷ lệ host nhiều listing trước QA là 1,0 vì dòng trùng); sai nằm ở test, không phải code, phát hiện khi chạy test.
- Kiểm chứng: 53 test của repo đạt (`python -m unittest discover -s tests -v`); chạy `scripts/run_qa.py` trên raw 4 mốc với 1.000 ID của nhóm:
  20 listing thiếu giá ở mốc cuối khớp data check, entire/private 875/125 khớp, 1.000 listing nằm đúng vùng chữ nhật workbook ở cả 4 mốc,
  số cột 79/85/90/90 khớp `reports/checks`. Số liệu trong `reports/sections/tv2.md` lấy từ các CSV do script sinh.

## Cập nhật 10/11/2026 — TV2: hình QA (`viz_qa.py`)

- Công cụ: Claude. Dùng để viết `src/airbnb/viz_qa.py`, `tests/test_viz_qa.py`, phần hình trong `scripts/run_qa.py`, `docs/QA.md`, `reports/sections/tv2.md`; đọc lại `docs/CONTRACTS.md`, `docs/IMPLEMENTATION_GUIDE.md`, `viz.py`, `run_pipeline.py` trước khi viết.
- Prompt chính: Hoàn thành viz.py (hình QA: tóm tắt QA, thiếu dữ liệu/drift, tác động lên KPI; chỉ dùng thư viện chuẩn).
- AI sai ở đâu (đã phát hiện khi chạy và nhìn hình):
  1. Lần vẽ đầu có chữ cột "Nhóm" đè lên ô, chú giải đè nhãn ngày ở hình thiếu dữ liệu, trục giá có vạch lẻ (62, 125, 188); đã sửa bố cục và đổi cách chọn vạch trục (`_axis`).
  2. `room_type_shares` ban đầu thêm nhãn "Khác / rỗng" giữa chừng nên các mốc có danh sách nhãn khác nhau; test `test_room_type_shares_fold_unknown_types_into_other` bắt được, đã tính nhãn trước.
  3. Kỳ vọng `_axis(1100)` trong test do AI tính sai (đúng là 1250 với bước 250); sai nằm ở test, không phải code.
  4. Sau khi đối chiếu với bài 12–14 (checklist 5 điểm kiểm tra biểu đồ, tiêu đề nêu kết luận, giới hạn cạnh kết luận), phát hiện AI đã viết tiêu đề hình chỉ gọi tên biểu đồ
     ("Tác động của QA lên KPI"), hình không ghi cỡ mẫu n và mốc chụp, chú thích chỉ ghi `tables[...]` thay vì nguồn dữ liệu, và `tv2.md` đặt phương pháp
     lên đầu, tiêu đề mục là chủ đề. Đã sửa: tiêu đề hình sinh từ số liệu (`headline_*`), thêm n và nguồn/giới hạn (`_source_note`), viết lại `tv2.md` theo thứ tự
     kết luận → bằng chứng → giới hạn.
  5. Câu "Giá thiếu ở mốc cuối không ngẫu nhiên" trong bản nháp của AI vượt quá dữ liệu (chỉ có tương quan với `availability_365`; chưa kiểm nguyên nhân) và có
     một câu thừa lặp ý; đã đổi thành "trong dữ liệu này, giá thiếu tập trung ở…" và tính lại: 15/15 listing có `availability_365 = 0` đều thiếu giá, 15/20 listing thiếu giá có `availability_365 = 0`, cả 20 là entire-home.
- Kiểm chứng: 76 test của repo đạt; tự tính lại từ `listings.csv.gz` thô theo ID của workbook (không qua `qa.py`) cho cả 4 mốc: n = 1.000, thiếu giá 69 / 1.000 / 28 / 20, median 174 / n/a / 189,4 / 213,545 CAD, room_type 875/125 mỗi mốc; chạy `scripts/run_qa.py` trên raw 4 mốc, mở cả 3 file SVG kiểm tay: 20 ô `price_missing_final` ở mốc cuối, thiếu giá
  6,9% / 100% / 2,8% / 2,0%, room_type 87,5% / 12,5% ở cả 4 mốc, supply 1.000 → 1.000 và median giá 174 / n/a / 189,4 / 213,5 CAD trước và sau QA, khớp `qa_report_listings.csv`.
