# AI usage

## Công cụ đã dùng (vào việc gì)
- OpenAI Codex: tạo starter repository từ tài liệu ZIP và đề bài, ngày 06/10/2026.
- Gemini API: adapter có sẵn; chưa chạy API và chưa có kết quả LLM thật khi tạo starter.

## Prompt then chốt
1. Yêu cầu tạo bộ khung repository nhóm 5 người, bốn snapshot Toronto, pipeline và Git workflow (run_pipeline.py, src/, docs/).
Nhóm bổ sung 5–10 prompt thực tế trong quá trình làm; không tạo prompt giả.

## AI sai ở đâu
Chưa ghi nhận ví dụ lỗi đã xác minh. Ghi ví dụ thật: file, lỗi, cách sửa, commit.

## Nhóm kiểm chứng thế nào
Starter có kiểm thử trên fixture giả. Nhóm phải kiểm chứng dữ liệu thật, giá trị KPI,
LLM, nhãn tay và giải thích toàn bộ code trước khi nộp. Không dùng số liệu demo trong báo cáo.

## Cập nhật 06/10/2026 — README nhóm 10
- Codex đối chiếu source local, bản phân công Markdown và đề bài; cập nhật README với
  remote GitHub nhóm, 16 URL dữ liệu, bảng owner/module và trạng thái phần còn thiếu.
- Bổ sung lại các dotfile setup/Git/CI đang thiếu trong bản repo Desktop.
- Prompt: kiểm tra chia code theo phân công, dùng code chung trên main/pull và viết README
  đúng nhóm, đường dẫn GitHub/dataset đầy đủ.
