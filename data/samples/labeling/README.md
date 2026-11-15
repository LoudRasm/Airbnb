# Phiếu gán nhãn đã chia sẵn

100 review từ cột Nhãn tay của workbook nhóm DSE2049-C01-G10-toronto, 20/người.
Text lấy nguyên bản mốc 2026-06-15; tất cả sentiment khởi tạo trống, không phải dự đoán AI.

| File | Người sửa |
|---|---|
| [tv1.json](tv1.json) | Dương Nhật Huy |
| [tv2.json](tv2.json) | Mai Anh Đức |
| [tv3.json](tv3.json) | Nguyễn Quốc Hiếu |
| [tv4.json](tv4.json) | Vũ Phạm Khánh Nam |
| [tv5.json](tv5.json) | Phan Ngọc Huy |

Mở bằng editor văn bản, chỉ điền sentiment/needs_review/note. Không sửa ID/comments/metadata,
không sửa manifest hoặc tạo lại phiếu; không dùng Excel. JSON không làm tròn ID chuỗi.

Đọc [hướng dẫn đầy đủ](../../../docs/MANUAL_LABELING.md) trước khi bắt đầu.
Kiểm riêng, ví dụ Đức: `python scripts/label_reviews.py check --member tv2` ở gốc repo.
Chỉ commit file của mình qua PR; TV5 ghép CSV cuối sau khi đủ cả 5 phần và nhóm trưởng duyệt.
