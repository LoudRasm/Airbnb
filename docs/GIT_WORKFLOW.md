# Branch → PR → merge → pull

Repo: [GitHub nhóm 10](https://github.com/uet-iai-notebook-labs-2026/2627-LTXLDL-Airbnb-dse2049_1-nhom10).
Mỗi thành viên làm trong cùng cấu trúc `src/airbnb/`, trên branch riêng. Merge là ghép thay đổi
Git vào `main`, không phải chép file từ folder cá nhân sang source chính.

## 1. Lấy main mới nhất và tạo branch

Chạy ở gốc repo sau khi cài môi trường theo [README](../README.md). Nếu chưa clone, làm bước
clone trong README một lần. Không chạy lại `git init` hoặc thêm lại remote `origin`.

```bash
git status
git switch main
git pull --ff-only origin main
git switch -c feat/tv2-qa
```

Nếu `git status` có công việc chưa commit, lưu/commit trên branch đang làm trước khi chuyển
nhánh. Không xóa thay đổi để ép pull chạy được. Nếu `--ff-only` báo hai nhánh phân kỳ, kiểm tra
lịch sử với nhóm trưởng, không dùng reset hoặc force-push để xử lý.

Tên branch gợi ý; thêm tên task khi một người có nhiều PR:

| Người | Branch | File chính |
|---|---|---|
| Nhóm trưởng | `feat/tv1-market` | `analysis.py`, `viz_market.py`, luồng chung |
| Đức | `feat/tv2-qa` | `qa.py`, `eda.py`, `viz_qa.py` |
| Hiếu | `feat/tv3-listings` | `kpi.py`, `viz_spatial.py` |
| Nam | `feat/tv4-calendar` | `calendar.py`, `viz_calendar.py` |
| Phan Huy | `feat/tv5-reviews` | reviews, baseline, LLM, evaluation, guest KPI/hình |

## 2. Triển khai và kiểm tra phần mình

Đọc [TEAM](TEAM.md), [hướng dẫn triển khai](IMPLEMENTATION_GUIDE.md) và [contracts](CONTRACTS.md).
Sửa đúng module được giao; viết test riêng và `reports/sections/tvN.md`.

```bash
python -m unittest discover -s tests -v
python run_pipeline.py --status
git diff --check
git diff
```

Pipeline còn TODO của người khác thì kiểm thử trực tiếp hàm của mình trên fixture nhỏ.
Không phải chạy được toàn pipeline mới mở PR. `--status` chỉ đọc trạng thái; CI nền xanh
chưa xác nhận thuật toán đúng. Demo cũng chưa chạy được khi các module cần thiết còn TODO.

## 3. Commit đúng file rồi push branch

Ví dụ Đức, sau khi đã tạo các file test và phần báo cáo tương ứng:

```bash
git add src/airbnb/qa.py src/airbnb/eda.py src/airbnb/viz_qa.py tests/test_qa.py docs/QA.md reports/sections/tv2.md
git diff --cached --stat
git diff --cached
git commit -m "feat(qa): implement and validate assigned-data rules"
git push -u origin feat/tv2-qa
```

Chỉ thêm file thực sự sửa; ví dụ trên không bắt buộc hoàn thành ba module trong một PR.
Nếu dùng AI, stage thêm `AI_USAGE.md`; nếu thêm thư viện, stage file khai báo phiên bản.
Không dùng `git add .` để gom cả thay đổi không liên quan. Không sửa tác giả commit để tạo
đóng góp thay người khác; mỗi người commit bằng tài khoản mình.

Raw, workbook, key và output phân tích tự sinh đang gitignore. Bàn giao code/test, lệnh chạy,
số liệu đối chiếu và diễn giải trong PR/phần báo cáo. Nếu cần lưu bảng sạch nhỏ dưới 50 MB,
nhóm trưởng kiểm tra rồi chỉ thêm đúng file bằng `git add -f <file>`.
Data check có các CSV/notes/chẩn đoán nhỏ được commit riêng theo [luồng kiểm tra](DATA_CHECK_WORKFLOW.md).

## 4. Mở PR vào main

Trên GitHub chọn **Compare & pull request**: base `main`, compare branch của mình.
Điền mẫu PR có sẵn: phần việc, hàm thay đổi, lệnh đã chạy, số liệu và việc còn thiếu.
Chọn reviewer theo TEAM.md và báo nhóm trưởng. Ảnh chỉ minh họa; không thay source/test/kết quả.

Reviewer kiểm logic, contract, phạm vi ID, xử lý lỗi, số liệu và phần báo cáo. Nếu module đã
hoàn thành, xác nhận việc bật `READY = True` trong branch trước merge. PR dở dang có thể để
Draft; module chưa hoàn thành vẫn `READY = False`. Xử lý góp ý bằng commit mới rồi push tiếp.

Nhóm trưởng merge khi reviewer đồng ý và CI đạt. Có thể dùng **Squash and merge** cho PR có
nhiều commit sửa nhỏ; GitHub vẫn lưu tác giả và cuộc review. Nếu thay giao diện hàm, cập nhật
pipeline, contract và test trong cùng PR hoặc một PR tích hợp đã thống nhất.

## 5. Nếu main thay đổi trong lúc đang làm

Đứng trên branch của mình:

```bash
git fetch origin
git merge origin/main
```

Nếu không conflict, Git hoàn tất merge; không cần tự commit thêm. Nếu có conflict:

1. Mở file Git báo, đọc hai phần giữa các dấu `<<<<<<<`, `=======`, `>>>>>>>`.
2. Ghép logic phù hợp rồi bỏ dấu conflict. File config/contract cần thống nhất với owner và nhóm trưởng.
3. Stage đúng file đã giải quyết và hoàn tất merge:

```bash
git add <file-da-giai-quyet>
git commit
python -m unittest discover -s tests -v
python run_pipeline.py --status
git push
```

Thay `<file-da-giai-quyet>` bằng đường dẫn thật. Nếu chưa quyết định được cách ghép, dùng
`git merge --abort` để quay về trạng thái trước merge rồi trao đổi nhóm. Không chọn toàn bộ
ours/theirs một cách máy móc và không force-push branch của người khác.

## 6. Sau khi PR đã merge

Khi branch không còn thay đổi chưa lưu:

```bash
git switch main
git pull --ff-only origin main
python -m unittest discover -s tests -v
python run_pipeline.py --status
```

Code đã merge nằm sẵn trong module; import của pipeline dùng phiên bản mới. Tạo branch mới
cho task tiếp theo. Branch cũ có thể xóa trên GitHub sau merge; nếu squash merge, việc xóa
branch local có thể cần kiểm tra lại vì lịch sử commit không trùng nguyên bản.

## Nhóm trưởng quản lý main và bài nộp

Nhóm trưởng giữ cấu hình, loader, contracts và thứ tự gọi trong `run_pipeline.py`.
Không chép implementation của thành viên vào pipeline. Đầu ra chung phải sinh được từ code
và dữ liệu trên mỗi máy. Pull không mang theo raw, workbook hoặc key của máy người khác.

Khuyến nghị mời đủ nhóm và giảng viên, để repo private, đặt quy tắc review/CI cho main.
Quyền truy cập và branch protection phải kiểm tra trên GitHub; tài liệu này không xác nhận
chúng đã được bật. Quy tắc làm việc nhóm là mở PR; thay đổi quản trị của nhóm trưởng xử lý theo
quyền và quy tắc thực tế của repo.

Trước nộp, clone sạch ở thư mục mới, dựng môi trường đúng README, chạy pipeline thật có LLM
và tái tạo số liệu/hình. Ghi mã commit source vào báo cáo, bổ sung báo cáo và commit cuối.
Chỉ khi mọi sản phẩm đã hoàn thành mới tạo tag tại commit nộp:

```bash
git switch main
git pull --ff-only origin main
git status
git rev-parse HEAD
git tag final
git push origin final
```

Đảm bảo cây làm việc sạch và report ghi rõ commit source dùng sinh số liệu. Nếu tag `final`
đã có, kiểm tra với nhóm trưởng; không tự ghi đè hoặc di chuyển tag đã nộp.
