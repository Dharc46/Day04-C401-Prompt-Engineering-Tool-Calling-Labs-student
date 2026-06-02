---
name: save
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [content, filename, format]
outputs: [filename, path, format, size_bytes]
side_effect: local_file_write
---
# save

Saves research results to a local file in the `saved/` directory.
Supports txt, md, and json formats. Auto-generates a timestamped filename
if none is provided. No external API needed.
