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
