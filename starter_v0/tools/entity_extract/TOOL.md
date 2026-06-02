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

Examples:

- Request:

	{
		"text": "OpenAI released GPT-4. Elon Musk and Sam Altman commented.",
		"top_k": 5
	}

- Response:

	{
		"entities": [
			{"text": "GPT", "count": 1},
			{"text": "Elon Musk", "count": 1},
			{"text": "Sam Altman", "count": 1}
		]
	}

Notes:
- This is a heuristic extractor intended for lightweight analysis; it will not replace a full NER model for production use.
