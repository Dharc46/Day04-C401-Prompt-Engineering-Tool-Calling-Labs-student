---
name: youtube
track: bonus
kind: live_api
provider: RapidAPI (YouTube)
requires_env: [RAPIDAPI_KEY]
inputs: [query, limit, sort_by]
outputs: [items]
side_effect: false
---
# youtube

Searches YouTube videos via RapidAPI. Supports sorting by relevance, date,
or viewCount. Uses RAPIDAPI_YOUTUBE_HOST env var (defaults to
youtube-search-and-download.p.rapidapi.com).
