# Luồng kiểm tra dữ liệu nhóm 10

Dùng cho báo cáo kiểm tra đầu vào của giảng viên. Mỗi thành viên chạy phần của mình cho **cả 4 mốc**.
Script đọc workbook và raw gốc, lọc đúng ID, xuất CSV và ghi chú để nhóm trưởng ghép.
Không cần pandas, Excel, notebook, API hoặc nhãn tay đã làm để hoàn thành bước kiểm tra này.

## Chuẩn bị một lần trên mỗi máy

1. Pull main mới nhất. Dùng Python 3.13.7 và môi trường theo README.
2. Giữ nguyên workbook giảng viên. Chép một bản vào `data/assignments/assignment.xlsx`;
   thư mục này được gitignore. Hoặc truyền `--assignment "/đường/dẫn/file.xlsx"` vào mỗi lệnh.
3. Raw của mỗi ngày nằm ở `data/raw/YYYY-MM-DD/{listings.csv.gz,calendar.csv.gz,reviews.csv.gz}`.
   Không đổi thành `calendarYYYY-MM-DD.csv.gz`. Không mở rồi lưu lại file gốc bằng Excel.
4. Kiểm tra `configs/data_check.json`: lớp `UET.DSE2049 1`, nhóm `10`, mã `DSE2049-C01-G10-toronto`.
   Ngày và danh sách ID được đọc trực tiếp từ workbook. Bốn ngày hiện tại:
   `2025-09-11`, **`2025-12-12`**, `2026-03-19`, `2026-06-15`.

Ví dụ dùng workbook tại đường dẫn khác (thay bằng đường dẫn của máy mình):

```bash
python scripts/check_data.py --part calendar --assignment "/path/to/assignment.xlsx"
```

## Lệnh theo đúng phân công

Đứng ở gốc repo, đã kích hoạt môi trường Python:

| Người | Lệnh | File bàn giao chính trong reports/checks/ |
|---|---|---|
| TV2 — Đức | `python scripts/check_data.py --part listings` | `listings_summary.csv`, `missing_columns.csv`, `listings_notes.md`, `listings_diagnostics.json` |
| TV3 — Hiếu | `python scripts/check_data.py --part listing-details` | `listing_details.csv`, `listing-details_notes.md`, `listing-details_diagnostics.json` |
| TV4 — Nam | `python scripts/check_data.py --part calendar` | `calendar_summary.csv`, `calendar_notes.md`, `calendar_diagnostics.json` |
| TV5 — Phan Huy | `python scripts/check_data.py --part reviews` | `reviews_summary.csv`, `review_sample_counts.csv`, `reviews_notes.md`, `reviews_diagnostics.json` |
| TV1 — bạn, nhóm trưởng | `python scripts/check_data.py --part merge` | `check_DSE2049-C01-G10-toronto.csv`, `report_answers.md`, `merge_status.json` |

Đức và Hiếu dùng cùng hàm lọc listings trong module chung; không cần chuyển dữ liệu đã lọc lớn qua Git.
Script/kết quả calendar Nam và listings Đức đã merge vẫn được giữ để lưu đóng góp.
Luồng chung hiện dùng `scripts/check_data.py`; Nam chạy `--part calendar` như bảng trên.
Terminal hiển thị tiến độ/trạng thái và đường dẫn đã lưu. **CSV/ghi chú là kết quả bàn giao**, không chụp ảnh terminal thay file.
Không bắt buộc dùng notebook để chạy kiểm tra.

Nhóm trưởng có thể chạy tất cả để kiểm chứng lại trước khi nộp:

```bash
python scripts/check_data.py --part all
```

Lệnh all chạy lại cả bốn phần và ghi đè các file kết quả tự sinh trong `reports/checks/`.
Nếu muốn giữ bản cũ, sao lưu hoặc commit trước. Không chỉnh tay các bảng số liệu tự sinh;
chỉ bổ sung diễn giải sau khi kiểm chứng. `report_answers.md` là bản gợi ý, câu 4 cần nhóm bổ sung
quyết định với các cột ngoài giá, câu 5 cần nhóm trưởng xác nhận.

## Quy tắc kiểm tra

- Listings: raw `id` thuộc sheet Listing của lớp + nhóm. Calendar: raw `listing_id` thuộc cùng danh sách.
- Reviews: raw `id` thuộc danh sách **review_id** trong sheet Review. Không lọc bằng listing_id.
- ID dài được giữ chính xác dạng chuỗi/số nguyên; không qua float.
- Cùng 5.000 review xuất hiện tại bốn mốc: đếm từng mốc riêng, không dedupe giữa các mốc cho bảng kiểm tra.
- Thống kê sau lọc ID, **trước cleaning**. Không xóa giá rỗng, dòng trùng hoặc thay giá bằng trung bình.
- Dung lượng byte là file gzip gốc đã tải, không phải bảng sau lọc.
- Cột rỗng/whitespace/NaN tính là thiếu. Số cột lấy từ header raw, không thêm cột helper.
- Giá chỉ dùng cho phân tích ở mốc cuối; `thieu_price` vẫn đếm cả bốn mốc. Calendar không kiểm giá.
- Câu 2 lấy trực tiếp dấu x trong hai cột workbook: **1.000 mẫu LLM / 100 nhãn tay**. Không gọi API.
- Calendar kiểm 365.000 dòng, 1.000 listing, 365 dòng/listing, khóa ngày không trùng, ngày hợp lệ và available t/f.
- Kỳ vọng dùng để kiểm chứng, **không điền thay số đo**. Lệch số thì xuất số thực tế, đánh dấu lỗi.

## Khi có lỗi và khi tổng hợp

Mỗi phần luôn xuất bốn dòng nếu workbook hợp lệ; file thiếu/không đọc được có status/error,
ô số đếm chưa xác định để trống, không giả thành 0. JSON chẩn đoán lưu danh sách ID thiếu.
`status=ok` chỉ áp dụng cho phần của người đó; không tự kết luận cả ba file đã tải đủ.

Exit code: `0` đạt các kiểm tra được triển khai; `1` đã xuất kết quả nhưng còn lỗi/lệch số;
`2` chưa bắt đầu được do workbook/config không hợp lệ. Đọc file notes sau mỗi lần chạy.

Lệnh merge kiểm mã nhóm, ngày, số đếm, phiên bản workbook và SHA256 raw.
Đức/Hiếu phải dùng cùng listings; số cột thiếu nhiều phải khớp danh sách tên cột.
Nhóm trưởng cần có đủ raw local để kiểm SHA256 khi merge, không chỉ các CSV của thành viên.

Nếu thiếu phần, lệch số hoặc raw/workbook đã đổi, merge xuất **`check_....draft.csv`** cùng
`ready_to_submit=false` trong merge_status.json; không xuất bản cuối và loại bản cuối tự sinh đã cũ.
Không nộp file draft; xem blocker, chạy lại phần liên quan rồi merge.
`ready_to_submit` chỉ xác nhận các kiểm tra số liệu của CSV đã đạt; câu trả lời vẫn cần người đọc duyệt
(`answers_need_human_review=true`). Khi tất cả đạt, file cuối có đúng 16 cột theo mẫu giảng viên và 4 dòng ngoài header;
`tai_ve_ok=co` được tổng hợp từ kết quả của các phần. Công cụ kiểm file local, không suy đoán mã HTTP từ lỗi đọc.

## Push kết quả đúng phần, tránh conflict

Mỗi người tạo branch/PR riêng. Ví dụ Nam:

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/nam-calendar-check
python scripts/check_data.py --part calendar
git add reports/checks/calendar_summary.csv reports/checks/calendar_notes.md reports/checks/calendar_diagnostics.json
# Nếu sửa logic, thêm đúng file code đã sửa vào git add
git commit -m "feat(calendar): add four-snapshot check results"
git push -u origin feat/nam-calendar-check
```

Mở PR vào main, đính kèm lệnh đã chạy và trạng thái đạt/lỗi. Chỉ commit file thuộc phần mình.
Không commit workbook, raw, filtered data lớn, API key hoặc notebook output.
Không cùng sửa báo cáo cuối: nhóm trưởng phụ trách merge và bản trả lời cuối.
Nếu phát triển logic trong `src/airbnb/data_check.py`, trao đổi owner, PR nhỏ và chạy tests:

```bash
python -m unittest discover -s tests -v
```

## Phân biệt với pipeline phân tích cả kỳ

`run_pipeline.py` hiện có loader lọc theo workbook và các module phân tích TODO theo owner.
Không dùng output sau QA hoặc kết quả sampling của pipeline để điền bảng kiểm tra đầu vào.
Luồng trong tài liệu này là `scripts/check_data.py`, đếm từng mốc trước cleaning và đọc
trực tiếp hai cột Mẫu LLM/Nhãn tay. Data check vẫn chạy dù các module phân tích chưa READY.
Các quyết định phân tích cả kỳ (KPI, LLM, giá, vùng) do owner triển khai theo CONTRACTS.
Vùng workbook là 8 hình chữ nhật A01–A08; không đồng nhất với neighbourhood hành chính.
