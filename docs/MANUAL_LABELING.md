# Gán nhãn tay 100 review — hướng dẫn cho cả 5 người

Phiên bản quy tắc **1.0**, ngày **15/11/2026**, nhóm UET.DSE2049 1 — 10,
mã **DSE2049-C01-G10-toronto**. Đây là hướng dẫn thao tác, không phải kết quả gán nhãn.
Phan Huy điều phối, nhóm trưởng duyệt bộ nhãn cuối.

## 1. Gán nhãn là làm gì?

Đọc nội dung khách viết trong `comments`, rồi tự chọn cảm xúc của review:
`positive`, `mixed` hoặc `negative`. Không phải sửa code phân tích, chạy Gemini hay gán dấu x.
Dấu x ở cột **Nhãn tay** chỉ chọn review cần đọc; dấu x không phải nhãn cảm xúc.

Workbook giao 5.000 review ID, trong đó 1.000 thuộc Mẫu LLM và đúng 100 thuộc Nhãn tay.
Nhóm chỉ gán nhãn cho **100 ID này một lần**, không phải 100 review cho từng snapshot.
Reviews được lọc theo review_id, không lọc thêm theo listing_id của nhóm.

## 2. Mở đúng phiếu của mình

Đã trích nguyên văn 100 review từ `reviews.csv.gz` mốc **2026-06-15**, chia theo ID tăng dần,
20 review/người. Lựa chọn này có thể tái lập; không chọn theo cảm xúc và không thay ID khó.
Phiếu JSON chứa sẵn review_id, listing_id, ngày và comments, nên người gán nhãn không cần
raw, workbook, API key hoặc pipeline chạy được. Đọc phiếu bằng VS Code/editor văn bản.

| Người | Phiếu chỉ người đó sửa | Branch gợi ý |
|---|---|---|
| TV1 — Dương Nhật Huy | [tv1.json](../data/samples/labeling/tv1.json) | `feat/tv1-manual-labels` |
| TV2 — Mai Anh Đức | [tv2.json](../data/samples/labeling/tv2.json) | `feat/tv2-manual-labels` |
| TV3 — Nguyễn Quốc Hiếu | [tv3.json](../data/samples/labeling/tv3.json) | `feat/tv3-manual-labels` |
| TV4 — Vũ Phạm Khánh Nam | [tv4.json](../data/samples/labeling/tv4.json) | `feat/tv4-manual-labels` |
| TV5 — Phan Ngọc Huy | [tv5.json](../data/samples/labeling/tv5.json) | `feat/tv5-manual-labels` |

Các phiếu hiện **để trống toàn bộ sentiment**. `manifest.json` lưu tập ID/phân công, phiên bản
guideline và checksum nguồn; không sửa hoặc tạo lại manifest trong branch cá nhân.
Không mở rồi lưu lại workbook/CSV gốc bằng Excel. Giữ ID trong JSON là chuỗi có dấu nháy,
không chuyển sang số, số thập phân hoặc dạng `1.23E+18`.

## 3. Quy tắc chọn nhãn

Đây là quy ước của nhóm, cần giữ nhất quán giữa người gán nhãn, baseline và LLM.
Đánh giá trải nghiệm lưu trú được thể hiện trong câu, không chỉ đếm từ positive/negative.

| Nhãn | Chọn khi | Ví dụ tự đặt để minh họa, không thuộc 100 review |
|---|---|---|
| `positive` | Có đánh giá tích cực, không có phàn nàn rõ ràng về trải nghiệm | “Clean apartment, helpful host. Would stay again.” |
| `mixed` | Có cả khen và chê có ý nghĩa về trải nghiệm | “Great location, but the room was dirty and noisy.” |
| `negative` | Phàn nàn/bất mãn rõ ràng, không có đánh giá tích cực đáng kể | “The room was dirty. I would not recommend it.” |

Lời lịch sự như “thanks” không tự biến review phàn nàn thành mixed. Chi tiết mô tả như
“10 phút đi bộ” không tự là lời chê nếu khách không thể hiện bất tiện. Một review vừa khen
vị trí vừa chê tiếng ồn vẫn mixed dù có nhiều từ khen; không dùng số câu để quyết định.
Không suy ra khen/chê từ việc review dài/ngắn, ngôn ngữ, tên khách hoặc tên chỗ ở.

Đọc kỹ phủ định và ngữ cảnh: “not clean” khác “clean”; “not bad” không tự là negative.
Nếu mỉa mai, chỉ kể sự việc trung tính, thiếu ngữ cảnh, chỉ có emoji hoặc không hiểu ngôn ngữ:
đánh dấu ca khó để thảo luận. **Mixed không phải nhãn mặc định cho trường hợp không hiểu.**
Không thêm nhãn `neutral`, `unknown`, `pos`, `1` vào bộ cuối vì pipeline chỉ nhận ba nhãn chuẩn.

Có thể dùng công cụ dịch để hiểu ngôn ngữ; giữ comments gốc và ghi rõ trong note nếu bản dịch
có thể ảnh hưởng quyết định. Không dùng LLM hoặc baseline chọn sentiment thay mình, và không
xem dự đoán của chúng trước khi hoàn tất nhãn tay. Nếu dùng AI hỗ trợ dịch, ghi trong AI_USAGE.

## 4. Điền phiếu từng review

1. Pull main mới nhất, tạo branch của mình theo Git workflow; mở đúng file JSON ở bảng trên.
2. Đọc trọn `comments`. ID/ngày chỉ để đối chiếu, không quyết định cảm xúc.
3. Chỉ sửa ba trường: `sentiment`, `needs_review`, `note`. Không đổi comments, ID, ngày,
   listing_id, member, source_snapshot hoặc guideline_version; không thêm/xóa review.
4. Ca rõ: điền nhãn đúng chữ thường, `needs_review: false`; note có thể ghi lý do ngắn.
5. Ca khó: đặt `needs_review: true`, ghi cụm từ/nguyên nhân chưa chắc trong note.
   Có thể để sentiment trống hoặc ghi nhãn tạm; ca này chưa đủ điều kiện ghép cuối.
6. Làm đủ 20 review, lưu UTF-8 và kiểm tra phiếu bằng lệnh ở phần tiếp theo.

Ví dụ ba trường cần điền cho một ca rõ (chỉ minh họa cú pháp):

```json
"sentiment": "positive",
"needs_review": false,
"note": "Khách khen phòng sạch và chủ nhà; không có phàn nàn."
```

Trong JSON: sentiment/note là chuỗi có dấu nháy kép; needs_review là `true`/`false` không có
dấu nháy. Giữ dấu phẩy giữa các trường; nếu note có dấu nháy kép bên trong, dùng `\"`.
Không dùng tìm-thay thế toàn bộ để điền cùng một nhãn cho 20 review.

## 5. Kiểm tra và gửi kết quả qua PR

Đứng ở gốc repo, kích hoạt `.venv` như README. Ví dụ Đức:

```bash
python scripts/label_reviews.py check --member tv2
git add data/samples/labeling/tv2.json
git diff --cached
git commit -m "data(labels): annotate TV2 assigned reviews"
git push -u origin feat/tv2-manual-labels
```

Đổi tv2/branch thành phần mình. Lệnh check chạy độc lập với calendar/pipeline, không cần raw,
workbook hoặc API. Mã thoát 0: đủ 20 nhãn hợp lệ, không còn needs_review; mã 1: đọc lỗi được liệt
kê để xử lý. Check chỉ kiểm định dạng/phạm vi, **không xác nhận cảm xúc do con người chọn đúng**.

Mở PR vào main, ghi số review đã gán, số ca khó và lệnh đã chạy. PR còn ca khó để Draft hoặc
ghi rõ chưa hoàn thành để Phan Huy review. Chỉ stage phiếu mình; chưa sửa `manual_labels.csv`.
Nếu làm đồng thời code, nên tách PR gán nhãn để dễ review. Không gửi ảnh terminal thay phiếu.

## 6. Xử lý bất đồng và khóa bộ nhãn

Phan Huy tổng hợp các review có needs_review và nhờ một người khác đọc độc lập trước khi
trao đổi. Thống nhất nhãn dựa vào văn bản/quy tắc, không dựa vào nhãn Gemini/baseline.
Nếu chưa thống nhất thì TV1 cùng TV5 chốt cách diễn giải; ca chưa chốt vẫn giữ needs_review.
Không loại hoặc thay review khó bằng một ID khác.

Sau khi chốt: sửa sentiment, đặt needs_review false, thêm note ghi nhãn tạm → nhãn cuối,
người tham gia và lý do; lịch sử Git giữ quá trình thay đổi. Nếu sửa quy tắc chung, tăng phiên
bản, ghi quyết định và rà lại cả 100 review chịu ảnh hưởng, không sửa ngầm riêng một ca.
Thay guideline_version của phiếu phải được cập nhật đồng bộ với manifest qua PR thống nhất.

TV5/TV1 đọc kiểm tra các ca rõ và ca khó đã giải quyết. Việc một người gán 20 review không
đủ để báo cáo inter-annotator agreement; chỉ tính chỉ số đó nếu có bộ nhãn độc lập chồng lặp.

## 7. TV5 ghép bộ cuối; TV1 duyệt

Sau khi cả 5 PR nhãn đã merge và ca khó đã xử lý, TV5 pull main, tạo branch tổng hợp:

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/tv5-merge-manual-labels
python scripts/label_reviews.py check
python scripts/label_reviews.py merge
git add data/samples/manual_labels.csv
git diff --cached
git commit -m "data(labels): consolidate 100 human-reviewed labels"
git push -u origin feat/tv5-merge-manual-labels
```

Mở PR để nhóm trưởng duyệt. Merge kiểm đủ 100 ID duy nhất đúng workbook, nhãn hợp lệ,
không còn needs_review, text/metadata không bị sửa và checksum workbook/raw còn khớp.
Lệnh dừng nếu thiếu/sai nhãn; không tự điền chỗ trống. Nó chưa cần pipeline/calendar chạy được.
TV5/TV1 cần workbook/raw gốc local để ghép; người gán nhãn riêng không cần chúng.

Đầu ra có đúng hai cột `review_id,sentiment` và 100 dòng dữ liệu. Đây mới là file pipeline đọc.
Comments, note và ca khó được lưu trong phiếu JSON để truy vết, không thêm cột vào CSV cuối.
Khi CSV đã có nhãn khác, công cụ không tự ghi đè; xuất ứng viên để duyệt diff:

```bash
python scripts/label_reviews.py merge --output reports/generated/manual_labels_candidate.csv
```

Chỉ thay bộ chính sau khi nhóm trưởng duyệt. Khóa một phiên bản nhãn trước đánh giá;
không sửa gold labels để tăng accuracy/F1. TV5 phải dùng đúng phiên bản comments đã gán nhãn
cho baseline và LLM; dedupe giữa mốc không được âm thầm đổi text của 100 review này.

## 8. Nguồn và tái lập phiếu

`manifest.json` ghi SHA256 workbook/raw, ngày nguồn và hash nội dung từng review.
Nguồn review: [Inside Airbnb Toronto, mốc 2026-06-15](https://data.insideairbnb.com/canada/on/toronto/2026-06-15/data/reviews.csv.gz).
Workbook giảng viên chỉ được đọc, không được mở-lưu lại; raw gốc tiếp tục gitignore.

`python scripts/label_reviews.py prepare` chỉ dành cho TV1/TV5 chuẩn bị một lần từ config và
workbook; phiếu đã có sẵn thì **không chạy lại**. Công cụ từ chối ghi đè phiếu đang tồn tại.
Nếu đổi nguồn/phân công, lập PR thống nhất và lưu lại bộ cũ để không mất công gán nhãn.

[Checklist mỗi người](FINAL_CHECKLIST.md) · [Quay lại README](../README.md).
