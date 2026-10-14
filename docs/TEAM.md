# Phân công nhóm 10

Thứ tự do nhóm trưởng chốt: TV1 Dương Nhật Huy; TV2 Mai Anh Đức; TV3 Nguyễn Quốc Hiếu;
TV4 Vũ Phạm Khánh Nam; TV5 Phan Ngọc Huy. Mỗi người phụ trách phần mình ở cả bốn mốc.

## Hai giai đoạn

**Data check đã làm xong:** giữ nguyên `assignment.py`, `data_check.py`, `scripts/check_data.py`,
config/checks, kết quả CSV/notes và tests. PR calendar của Nam và các script/kết quả listings của Đức đã merge cũng giữ nguyên.
Không biến phần này thành TODO và không dùng nó thay cho QA/phân tích cả kỳ.

**Bài phân tích cả kỳ:** các file dưới đây hiện là khung TODO, chưa có thuật toán hoàn chỉnh.
Tên và chữ ký hàm thống nhất để nhóm trưởng gọi qua import.

| Người | File trong src/airbnb/ | Nhiệm vụ tự triển khai | Reviewer |
|---|---|---|---|
| TV1 — Dương Nhật Huy | loading.py, download.py, io.py, analysis.py, viz_market.py; run_pipeline.py ở gốc | Config/tải/loader/import đã có nền; còn market evolution và hình, tích hợp PR | Nam |
| TV2 — Mai Anh Đức | qa.py, eda.py, viz_qa.py | QA rules, cleaning/types/flags/drift, data dictionary, tác động KPI và hình QA | Hiếu |
| TV3 — Nguyễn Quốc Hiếu | kpi.py, viz_spatial.py | Giá mốc cuối, entire-home/host share, vùng/map, denominator và giới hạn mẫu | Nhóm trưởng |
| TV4 — Vũ Phạm Khánh Nam | calendar.py, viz_calendar.py | Streaming, availability 30/90 ngày, coverage, temporal; không dùng giá calendar | Phan Huy |
| TV5 — Phan Ngọc Huy | reviews.py, baseline.py, llm.py, evaluate.py, review_kpi.py, viz_reviews.py | Review dedupe, mẫu được giao, API/cache/retry, đối chứng/evaluation, guest KPI/hình | Đức |

Mỗi người tự thêm `tests/test_qa.py`, `test_listings.py`, `test_calendar_analysis.py`,
`test_reviews.py` hoặc tên tương ứng; tự viết `reports/sections/tvN.md`.
Không cùng sửa một file viz lớn; mỗi người đã có file riêng. `viz.py` chỉ nối imports.

## Hợp tác và hoàn thành task

Đức thống nhất cleaned schema để các bạn dùng chung; các bạn có thể phát triển với sample/fixture
và contract trong lúc QA chưa xong. Đổi chữ ký/cột phải thống nhất nhóm trưởng và downstream.
Mỗi thành viên triển khai logic, kiểm số liệu, thêm test phù hợp, cập nhật AI_USAGE nếu dùng AI,
push branch và được người khác review trước merge. Chỉ sau đó mới đặt module `READY = True`.

Nhãn tay: theo workbook hiện tại, 100 ID đánh dấu x nằm trong 1.000 mẫu LLM.
Phan Huy tổ chức guideline và phân việc gán nhãn cho cả nhóm. Mục tiêu 200 review trong kế hoạch
cũ là mở rộng nội bộ nếu nhóm chọn làm thêm; không thay số 1.000/100 của báo cáo data check.
Tất cả phải giải thích được toàn bộ sản phẩm khi vấn đáp.

[Hướng dẫn TODO/import/PR](IMPLEMENTATION_GUIDE.md) · [Contracts](CONTRACTS.md)
