# TV1 — Phân tích biến động trong cohort listing

Dương Nhật Huy · nhóm UET.DSE2049 1 — 10 · DSE2049-C01-G10-toronto.
Kiểm chứng độc lập ngày 15/11/2026. Bốn mốc theo workbook: 2025-09-11, 2025-12-12,
2026-03-19, 2026-06-15. Phần này không phải báo cáo tổng hợp cuối của cả nhóm.

## Bên nhận phân tích và câu hỏi

Giữ định hướng kế hoạch gốc: **nhóm theo dõi thị trường lưu trú ngắn hạn và du lịch Toronto**,
một bên nhận phân tích giả định trong bài học, không phải đơn vị thực tế đã đặt hàng.
Tên/vai trò/mục đích được ghi trong `configs/toronto.yaml`.

TV1 trả lời: dữ liệu có theo dõi đủ cùng tập ID qua các mốc không; trong các listing ghép được,
host_id và loại phòng thay đổi ra sao? Kết quả giúp xác định trường cần kiểm chứng sâu khi
đọc KPI không gian, availability và trải nghiệm do các thành viên khác phụ trách.

## Phương pháp và định nghĩa

Phạm vi là đúng **1.000 listing ID trong workbook**, không phải toàn bộ listing Toronto.
Ghép theo `(snapshot_date, listing_id)` và so sánh các mốc liền kề theo thứ tự cấu hình.
ID giữ dạng chuỗi; khóa trùng gây lỗi thay vì tự chọn một dòng. Không tính giá/calendar/LLM.

| Chỉ số | Công thức / xử lý |
|---|---|
| Coverage | Listing quan sát / toàn bộ ID phân công; ID vắng ở mọi mốc vẫn thuộc mẫu số |
| Host quan sát | Số host_id dạng chuỗi chữ số khác nhau trong cohort của một mốc |
| Host-ID change rate | Listing giữ lại có host_id khác / listing giữ lại có host_id hợp lệ ở cả hai mốc |
| Room-type change rate | Listing giữ lại có room_type khác / listing giữ lại có giá trị room_type không rỗng ở cả hai mốc |
| New / disappeared | ID xuất hiện thêm / không còn quan sát trong dữ liệu đầu vào so với mốc trước; chỉ là chẩn đoán hiện diện |

Host ID thiếu/sai dạng không vào mẫu số so sánh host; số cặp bị loại được xuất riêng.
Mẫu số 0 cho giá trị N/A (`None`, ô CSV trống), không giả thành tỷ lệ 0%.
Hàm `churn` và tên `kpi_churn.csv` được giữ để tương thích luồng cũ, nhưng không dùng để
ước tính tỷ lệ gia nhập/rời thị trường. Các cột entry_rate/exit_rate chỉ là tỷ lệ hiện diện
mới trên current_n và vắng trên previous_n trong dữ liệu quan sát.

## Lệnh chạy và đầu ra

```bash
python -m unittest discover -s tests -p test_tv1.py -v
python scripts/run_tv1.py --demo
python scripts/run_tv1.py --config configs/toronto.yaml
# Khi bảng sạch chung đã được tạo và kiểm chứng:
python scripts/run_tv1.py --config configs/toronto.yaml --listings data/processed/real/listings.csv
```

Chạy độc lập không import calendar, qa, kpi hoặc reviews của thành viên; không tải/gọi API.
Mặc định đọc ID/host_id/room_type từ raw đã lọc workbook bằng loader chung. Đây là phép chiếu
thuộc tính để kiểm chứng riêng TV1, **chưa thay cho chạy sau QA trong pipeline toàn nhóm**.
`--listings` nhận bảng sạch đã có; ở pipeline chung, TV1 nhận cleaned listings của Đức.

| File tự sinh | Nội dung |
|---|---|
| `data/processed/real/tv1/kpi_cohort.csv` | Coverage, số host quan sát, thuộc tính thiếu theo từng mốc |
| `data/processed/real/tv1/kpi_cohort_transitions.csv` | 3 khoảng so sánh, số cặp/mẫu số và tỷ lệ thay đổi |
| `figures/real/tv1/tv1_cohort_coverage.svg` | Hình mức bao phủ, kèm mẫu số phân công |
| `figures/real/tv1/tv1_host_changes.svg` | Hình thay đổi host_id, kèm số cặp và cặp bị loại |
| `reports/generated/real/tv1/run_metadata.json` | Input stage, checksum workbook/config/raw/code và phiên bản Python |
| `reports/generated/real/tv1/summary.md` | Bảng tóm tắt tái lập từ kết quả tính |

Demo dùng dữ liệu giả riêng, ghi vào nhánh demo và không được dùng cho kết luận Toronto.
Output đang gitignore; clone repo rồi chạy lệnh trên để tạo lại. SVG không cần thư viện ngoài.

## Kết quả trên raw được giao

| Mốc | Listing / phân công | Coverage | Host ID khác nhau, hợp lệ |
|---|---|---|---|
| 2025-09-11 | 1.000 / 1.000 | 100% | 930 |
| 2025-12-12 | 1.000 / 1.000 | 100% | 930 |
| 2026-03-19 | 1.000 / 1.000 | 100% | 937 |
| 2026-06-15 | 1.000 / 1.000 | 100% | 930 |

Không có host_id không dùng được hoặc room_type rỗng trong phần chiếu thuộc tính này.
Mỗi khoảng có 1.000 listing giữ lại, không có ID mới/vắng và đủ 1.000 cặp so sánh thuộc tính.

| Khoảng | Độ dài | Listing đổi host_id | Tỷ lệ | Listing đổi room_type |
|---|---|---|---|---|
| 2025-09-11 → 2025-12-12 | 92 ngày | 3 / 1.000 | 0,3% | 0 / 1.000 |
| 2025-12-12 → 2026-03-19 | 97 ngày | 35 / 1.000 | 3,5% | 0 / 1.000 |
| 2026-03-19 → 2026-06-15 | 88 ngày | 37 / 1.000 | 3,7% | 0 / 1.000 |

Các số trên được tính lại từ raw bằng code TV1, không chép hằng số từ báo cáo QA.
Chúng khớp số thay đổi host_id mà Đức đã báo cáo, là một đối chiếu độc lập trong cùng phạm vi.

## Phát hiện và giới hạn

Cùng 1.000 listing được theo dõi đủ bốn mốc nhưng host_id vẫn thay đổi. Hai khoảng sau có
nhiều thay đổi thuộc tính được ghi nhận hơn khoảng đầu; số host khác nhau cũng không cố định.
Điều này gợi ý cần kiểm tra việc gán host theo từng snapshot, không ghép một host_id cố định
cho listing suốt kỳ. Loại phòng không đổi trong những cặp quan sát được.

Coverage 100% và số ID mới/vắng bằng 0 phản ánh thiết kế cohort, không chứng minh nguồn cung
toàn Toronto không đổi. host_id đổi có thể do cập nhật tài khoản/ghi nhận dữ liệu; chưa đủ
chứng minh đổi chủ sở hữu, chuyển giao kinh doanh hoặc nguyên nhân pháp lý nào.
Khoảng thời gian dài ngắn khác nhau; tỷ lệ trên là trên từng khoảng, không phải tốc độ theo ngày.
Snapshot cũng không quan sát mọi thay đổi xảy ra rồi quay lại giữa hai lần chụp.

Kết quả riêng được tạo từ projection raw. Khi Đức/Hiếu/Nam/Phan Huy đã hoàn thiện và merge,
TV1 cần chạy lại luồng chung sau QA, đối chiếu tác động lọc dòng và ghép vào báo cáo cuối.
Không dùng phần này để thay KPI giá/host-share, calendar hoặc LLM của owner khác.

## Kiểm thử và bàn giao

**14 tests TV1 đạt:** phạm vi ID/mẫu số phân công, conservation hiện diện, ghép cặp và giá trị
thiếu, mẫu số 0, ID dài, trùng khóa, ngày/thứ tự mốc, không sửa input, số liệu trong SVG,
input raw/cleaned và lệnh demo từ ngoài repo. Đã xem ảnh render của cả hai SVG thật, không cắt
chữ/cột. Full integration vẫn bị lỗi calendar của Nam; không sửa module đó trong phần này.

`IMPLEMENTED=True` cho analysis/viz_market; `READY=False` giữ đúng bước chờ Nam review.
Sau peer review có thể bật READY bằng commit riêng; không coi cờ này là thuật toán chưa viết.
20 nhãn tay của TV1 vẫn để người học tự đọc/chốt, không dùng AI tạo gold labels.
Các bước QA liên mốc, nhãn toàn nhóm, full pipeline, PDF cuối và tag final vẫn thuộc finalize sau.

Nguồn: workbook gốc giảng viên và [Inside Airbnb Toronto](https://data.insideairbnb.com/canada/on/toronto/),
đúng các mốc được giao. Mã và checksum nguồn có trong run_metadata.json; dùng commit source
chứa module TV1 đã hoàn thiện để tái lập phần này. AI hỗ trợ code được khai báo trong AI_USAGE.
