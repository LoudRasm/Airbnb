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
  trong `tests/test_tv5.py` đạt; `READY = False`, `IMPLEMENTED = True` chờ TV2 (Đức) review.
