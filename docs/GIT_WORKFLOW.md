# Git workflow

Repository nhóm 10 đã có Git và remote `origin`:
[2627-LTXLDL-Airbnb-dse2049_1-nhom10](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10).
Không chạy lại `git init` hoặc `git remote add origin` trong repo này.
Nhóm trưởng xem phần đưa bộ khung lên main trong [README](../README.md).
Pull chỉ lấy code đã commit/push, không lấy raw hoặc key của người khác.

Mời nhóm và giảng viên; bật branch protection cho main, yêu cầu ít nhất một approval,
CI Starter checks pass, chặn direct push. Cấu hình này phải làm trên GitHub; chưa được xác minh từ repo local.

Mỗi task tạo một branch ngắn, ví dụ `feat/tv2-qa-price`, `feat/tv4-calendar-90d`:

```bash
git clone https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10.git
cd 2627-LTXLDL-Airbnb-dse2049_1-nhom10
git switch main
git pull --ff-only origin main
git switch -c feat/tv2-qa-price
# sửa module của mình; chạy test + demo
python -m unittest discover -s tests -v
python run_pipeline.py --demo --skip-llm
git add src/airbnb/qa.py tests/ docs/QA.md
git commit -m "feat(qa): flag invalid nightly prices"
git push -u origin feat/tv2-qa-price
```

Mở PR trên GitHub: ghi vấn đề, thay đổi, input/output và bằng chứng chạy. Reviewer khác tác giả.
Leader squash merge sau approval + CI. Xóa branch sau merge; tránh PR quá nhiều module.

Cập nhật branch trước review nếu main đổi:

```bash
git fetch origin
git merge origin/main
# giải conflict, giữ cả hai logic phù hợp; không chọn toàn bộ ours/theirs một cách máy móc
python -m unittest discover -s tests -v
python run_pipeline.py --demo --skip-llm
git add PATHS_YOU_RESOLVED
git commit
git push
```

Nếu không conflict merge tự tạo commit, bỏ lệnh git commit. Không force-push branch của người khác.
Nếu conflict config/contract: trao đổi owner và leader trước khi quyết định.
Sau merge: `git switch main` rồi `git pull --ff-only origin main` và tạo branch task mới.
Không chia sẻ notebook đang cùng chỉnh; clear notebook output trước commit.
Không commit generated output, raw hoặc key; thêm processed thật chỉ sau kiểm tra <50 MB.

Final: clone sạch, chạy pipeline thật có LLM, xác nhận mọi output, ghi commit trong report.
Sau đó `git tag final` và `git push origin final`. Không di chuyển tag final sau khi nộp.
