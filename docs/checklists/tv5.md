# TV5 — Phan Ngọc Huy

Cập nhật 2026-11-16 · Reviews/LLM. [Checklist chung](../FINAL_CHECKLIST.md).

Reviews theo review_id độc lập; nhãn tay có đủ 100; runner dùng đường dẫn nhãn config, mặc định đọc cache; KPI vùng có join nguồn.

- [x] Phiếu 20 review đã có; nhãn hiện tại giữ nguyên, không gán lại để tối ưu mô hình.
- [ ] Tạo cache Gemini thật 1.000 ID bằng lệnh riêng; kiểm --check, commit cache; chạy pipeline đầy đủ không key; phân tích lỗi, chi phí và kết quả 100 nhãn.
- [ ] Review phần code/kết quả liên quan, đối chiếu phần báo cáo của mình và giải thích được luồng chung.

Các thay đổi tiếp theo vẫn qua branch → test → PR → review/merge. Không dùng test dữ liệu giả làm kết quả phân tích thật.
