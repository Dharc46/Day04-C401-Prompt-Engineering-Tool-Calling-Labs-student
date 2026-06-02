---
name: source_rank
track: core
kind: local_formatter
provider: local
requires_env: []
inputs: [items, query, top_k, prefer_primary]
outputs: [items, query, item_count]
side_effect: false
---

# source_rank

Ranks and deduplicates retrieved source items using lightweight local heuristics.

Use this after `lookup`, `fetch`, `papers`, or other retrieval tools when the user
asks to prioritize sources, remove duplicates, or choose the strongest sources
for a digest/report.

It does not call external APIs and does not verify factual correctness. It only
scores the source metadata and summaries already provided to it.
