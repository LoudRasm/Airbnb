# TV2 — Mai Anh Đức

Đã xác nhận ngày 15/11: code QA/EDA và phần báo cáo đã có, 42 test QA đạt. Không cần viết lại
toàn bộ. [Checklist chung](../FINAL_CHECKLIST.md) · Reviewer: Hiếu, TV1 duyệt tích hợp.

- [ ] Gán 20 review trong [tv2.json](../../data/samples/labeling/tv2.json) theo [guideline](../MANUAL_LABELING.md).
- [ ] Chạy `python scripts/label_reviews.py check --member tv2`, gửi phiếu qua PR riêng.
- [ ] Hoàn thiện `src/airbnb/viz_qa.py`: hình QA/missingness/drift hoặc tác động KPI có câu hỏi rõ; nhận tables và trả list[Path], không tự tải lại raw.
- [ ] Test `eda.profile` và hình: nhiều cờ trên một listing, dòng không cờ, mốc/vùng rỗng; số trên hình khớp bảng.
- [ ] Chốt với TV1 cách đưa các bảng missingness/KPI impact/schema/cross-snapshot vào tables cho hình dùng. Pipeline hiện chưa gọi đầy đủ `run_listings_qa`/helper liên mốc.
- [ ] Bàn giao cleaned schema ổn định cho Hiếu/Nam/Phan Huy, ghi rõ types, flags và mẫu số trước/sau QA; không ghi đè logic KPI của owner khác.
- [ ] Kiểm GeoJSON theo từng mốc: báo cáo hiện nêu mới đối chiếu mốc đầu. Ghi rõ coverage/cột thật, không lặp giả định thiếu neighbourhood từ starter cũ.
- [ ] Rà nhận định “chỉ listing còn nhận đặt chỗ” hoặc “thiếu giá không ngẫu nhiên” trong tv2.md: số quan sát có thể cho thấy liên hệ, chưa đủ chứng minh cơ chế nguyên nhân hay toàn bộ khả năng đặt chỗ.
- [ ] Thống nhất bản chính của dictionary/rule catalog giữa reports/ và reports/sections/ để TV1 không lấy bản cũ; giữ lệnh tái tạo.
- [ ] Cập nhật `reports/sections/tv2.md` theo hình/kiểm chứng mới; ghi rõ hình QA là lựa chọn phân tích của nhóm, không bắt buộc tên file theo đề.
- [ ] Chạy test QA, EDA/hình riêng; chỉ bật READY từng module khi đủ logic/test/review. Không cần bật tất cả ba file đồng thời nếu một file còn dở.
- [ ] PR ghi lệnh, số liệu, đường dẫn output, giới hạn và phần TV1 cần nối; cập nhật AI_USAGE nếu dùng AI.

Lệnh có thể chạy độc lập khi calendar lỗi:

```bash
python -m unittest discover -s tests -p test_qa.py -v
python scripts/run_qa.py --config configs/toronto.yaml --out reports/generated/tv2-review
```

`--out` xuất vào folder riêng để tránh ghi đè bảng sạch chung. Nếu thêm tests EDA/hình,
ghi lệnh chạy tương ứng trong PR. Không báo full suite pass trước khi lỗi calendar được sửa.
