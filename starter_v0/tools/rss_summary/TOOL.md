---
name: rss_summary
summary: "Tóm tắt nội dung từ một RSS/Atom feed, trả về danh sách bài viết (title, url, summary)."
---

Tool `rss_summary` lấy một RSS/Atom feed public và trả về các mục tiêu biểu (title, url, summary).

Arguments:
- `url` (string, required): feed URL
- `limit` (integer, optional): số mục tối đa trả về (mặc định 5)

Behavior:
- Nếu feed hợp lệ, trả về danh sách item với `title`, `url`, `summary`.
- Nếu lỗi (không tải được hoặc parse thất bại), trả về `error` field.
