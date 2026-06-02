---
name: github_search
track: bonus
kind: live_api
provider: GitHub
requires_env: []
inputs: [query, sort, limit]
outputs: [items, total_count]
side_effect: false
---
# github_search

Searches GitHub repositories via the public REST API.
Free, no authentication needed. Supports sorting by stars, updated, or forks.
