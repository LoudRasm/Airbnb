# TV4 — Vũ Phạm Khánh Nam

Ưu tiên PR sửa import/cú pháp trước để mở lại status và integration. Lỗi được ghi nhận,
**chưa sửa thay Nam**. [Checklist chung](../FINAL_CHECKLIST.md) · Reviewer: Phan Huy, TV1 tích hợp.

- [ ] Gán 20 review trong [tv4.json](../../data/samples/labeling/tv4.json) theo [guideline](../MANUAL_LABELING.md).
- [ ] Chạy `python scripts/label_reviews.py check --member tv4`, gửi phiếu qua PR riêng.
- [ ] Sửa dòng tên branch sót trong calendar.py: `feat/tv4-calendar-analysis` ngay sau def aggregate và `main` cuối file; kiểm lại toàn bộ nội dung sau merge thay vì chỉ xóa marker.
- [ ] Bổ sung import thực sự dùng (`Counter`, `date`, `timedelta`); dựng lại thân aggregate/docstring đúng phạm vi, loại code TODO/dead code sót từ hai nhánh.
- [ ] Bỏ `calculate_weekend_pricing_premium` và mọi output/diễn giải giá calendar. Dữ liệu nhóm không có giá calendar để phân tích.
- [ ] Hoàn thiện `aggregate(records, snapshot, window_days, listing_ids)`: iterator streaming, cửa sổ [snapshot, snapshot+window_days), lọc ID, xử lý ngày/available/trùng và issue counts.
- [ ] Chốt mẫu số/coverage cho listing không có ngày quan sát hoặc ngày lỗi; không tự coi ngày thiếu là available/f hoặc bỏ listing mất calendar làm coverage đẹp hơn.
- [ ] Hoàn thiện `metrics(calendar, listings, cfg)` theo vùng/thời gian, đúng schema. Unavailable không phải booked/occupancy.
- [ ] Nếu làm cả 30/90 ngày, thống nhất TV1 cách gọi thật và phân biệt window trong output; config hiện chỉ truyền 90. Không duyệt cùng iterator hai lần vì lần sau đã cạn.
- [ ] Hoàn thiện `viz_calendar.render`: hình availability/coverage theo thời gian/vùng, lưu file và trả list[Path].
- [ ] Thêm `tests/test_calendar_analysis.py`: import được, biên cửa sổ, ID lạ, ngày/available lỗi, trùng, mất ngày, mẫu số 0 và từng cửa sổ.
- [ ] Viết `reports/sections/tv4.md` và ghi lệnh/số liệu/giới hạn; chỉ bật READY khi logic/test/review đủ.

Chạy theo thứ tự sau khi tự sửa:

```bash
python -m py_compile src/airbnb/calendar.py
python -m unittest discover -s tests -p test_calendar_analysis.py -v
python run_pipeline.py --status
python -m unittest discover -s tests -v
```

Status chạy được chỉ chứng minh import đã thông; pipeline có thể vẫn báo TODO các bạn khác.
PR calendar phải giữ script/kết quả data check đã hoàn thành và không sửa module cá nhân khác
để vượt test. Nếu phát hiện lỗi khác, ghi blocker và trao đổi owner.
