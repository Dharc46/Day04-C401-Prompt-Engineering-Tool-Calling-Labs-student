---
name: entity_extract
summary: "Trích xuất thực thể (organization, person, product) đơn giản từ văn bản đầu vào bằng heuristic." 
---

Tool `entity_extract` nhận `text` và trả về danh sách thực thể quan trọng (string) với tần suất.

Arguments:
- `text` (string, required): văn bản để trích xuất
- `top_k` (integer, optional): số thực thể hàng đầu trả về (mặc định 10)

Behavior:
- Sử dụng heuristic: nhóm các từ viết hoa liên tiếp làm một thực thể, đếm tần suất, trả về top_k.
