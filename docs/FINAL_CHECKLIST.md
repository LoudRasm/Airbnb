# Checklist hoàn thiện → PR/merge → nhóm trưởng finalize

Đối chiếu ngày **15/11/2026**, trên main **0df65f5** trước thay đổi tài liệu/gán nhãn này.
Đây là danh sách việc để mỗi người tự hoàn thành, không phải bản sửa lỗi thay thành viên.
Các ô chưa đánh dấu là việc cần xác nhận; không suy ra tỷ lệ hoàn thành chỉ từ READY.

## Mỗi người bắt đầu ở đây

| Người | Checklist riêng | Gán nhãn |
|---|---|---|
| Bạn — TV1 | [tv1.md](checklists/tv1.md) | [tv1.json](../data/samples/labeling/tv1.json), 20 review |
| Đức — TV2 | [tv2.md](checklists/tv2.md) | [tv2.json](../data/samples/labeling/tv2.json), 20 review |
| Hiếu — TV3 | [tv3.md](checklists/tv3.md) | [tv3.json](../data/samples/labeling/tv3.json), 20 review |
| Nam — TV4 | [tv4.md](checklists/tv4.md) | [tv4.json](../data/samples/labeling/tv4.json), 20 review |
| Phan Huy — TV5 | [tv5.md](checklists/tv5.md) | [tv5.json](../data/samples/labeling/tv5.json), 20 review |

Đọc [hướng dẫn gán nhãn](MANUAL_LABELING.md), làm đúng file mình, không cùng sửa CSV cuối.
Cả nhóm chỉ cần 100 ID được giao; không chia mỗi người một snapshot.

## Hiện trạng đã kiểm tra trực tiếp

- Đức: `qa.py`, `eda.py`, `scripts/run_qa.py`, test và phần báo cáo đã có; **42 test QA đạt**.
  Hình QA còn TODO; các kiểm tra QA giữa mốc/missingness/KPI impact cần nối đủ vào luồng chung.
- Nam: `calendar.py` có dòng tên branch sót sau merge, thiếu import và còn logic giá calendar.
  `run_pipeline.py --status` đang lỗi IndentationError ở calendar; module metrics/hình chưa xong.
- Hiếu/Phan Huy/TV1: các module phân tích được giao còn TODO theo file hiện tại.
- `manual_labels.csv` chỉ có header. Phiếu 5×20 mới chuẩn bị có text nhưng **chưa có nhãn tay**.

Không coi các ghi nhận trong báo cáo phân tích cũ là kết quả mới nếu chưa đo lại. Ví dụ:
`reports/sections/tv2.md` đã ghi có neighbourhood hợp lệ, nên Hiếu cần kiểm coverage từng mốc;
không mặc định khẳng định toàn bộ cột thiếu theo ghi chú khung trước đây.

## Việc chung trước khi PR phần mình đủ điều kiện merge

- [ ] Giữ tên hàm/schema theo CONTRACTS; nếu thay đổi, cập nhật hợp đồng/writer/test và thống nhất TV1.
- [ ] Thực hiện đúng phạm vi ID, ngày, giá mốc cuối; không dùng giá calendar hoặc lọc reviews theo listing ID.
- [ ] Test trực tiếp module của mình, có ca dữ liệu lỗi và kết quả kỳ vọng rõ; ghi lệnh/kết quả trong PR.
- [ ] Xuất được CSV/hình từ code; ghi đường dẫn và diễn giải vào `reports/sections/tvN.md`.
- [ ] Chỉ bật READY cho module đã triển khai đầy đủ và được review; không trả bảng giả để vượt kiểm tra.
- [ ] Ghim dependency mới, cập nhật tài liệu/AI_USAGE khi liên quan; chỉ stage file thuộc task.
- [ ] Người khác review logic/số liệu; xử lý góp ý trước khi nhóm trưởng merge.

PR gán nhãn có thể kiểm độc lập khi calendar còn lỗi. PR code khác cũng có thể chuẩn bị/test
riêng; nếu full CI còn đỏ do lỗi nền, ghi đúng blocker, không nói đã pass toàn bộ và không bỏ
test hoặc tắt CI để merge. Nhóm trưởng ưu tiên PR Nam sửa lỗi import trước khi tích hợp toàn luồng.

## Thứ tự tích hợp đề xuất

1. Cả nhóm gán nhãn song song với code. Nam tự sửa lỗi import/cú pháp để mở lại kiểm tra chung.
2. Đức chốt cleaned schema/QA; Hiếu và Nam triển khai KPI/hình dựa trên schema đó.
3. Phan Huy hoàn thiện reviews/baseline/LLM/evaluation; thu đủ nhãn và xử lý bất đồng bằng người đọc.
4. PR riêng từng phần vào main; TV5 ghép CSV nhãn qua PR được TV1 duyệt.
5. Sau khi các phần đã merge, TV1 tích hợp lời gọi còn thiếu, chạy dữ liệu thật và finalize.

## Chốt cuối chỉ do TV1 điều phối

- [ ] Xem đủ checklist cá nhân và PR; pull main, kiểm sạch diff và toàn bộ tests/status.
- [ ] Xác minh toàn bộ 100 nhãn đúng ID/text, đã duyệt; baseline/LLM đánh giá cùng tập nhãn.
- [ ] Chốt bên nhận phân tích, bộ KPI và ý nghĩa biến động trong cohort; không suy rộng toàn Toronto.
- [ ] Nối QA liên mốc, missingness, impact và kiểm neighbourhood đúng từng mốc; xuất đủ báo cáo.
- [ ] Chạy pipeline thật đầy đủ LLM; đối chiếu CSV/hình, mẫu số, tiền CAD và mọi kết luận trong report.
- [ ] Đối chiếu bộ đầu ra cuối với [đề bài](https://courses.iaidev.com/programming-for-data-processing/2627-1/projects/project_airbnb.html),
  môi trường cài lại được, AI_USAGE và báo cáo PDF; mọi thành viên giải thích được toàn sản phẩm.
- [ ] Thử clone sạch, tái tạo bằng cấu hình/khóa môi trường khác; xác minh cách chấm mốc ngoài workbook.
- [ ] Chỉ khi bản nộp đạt mới ghi commit source, commit báo cáo và tạo tag final. Không tạo tag ở giai đoạn checklist này.

Hạn trang đề đang ghi: **23:59 ngày 22/11/2026**; nếu có thông báo riêng mới hơn trên Canvas,
nhóm trưởng đối chiếu trước khi nộp. [Git workflow](GIT_WORKFLOW.md) · [Phân công](TEAM.md).
