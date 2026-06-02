---
name: trending
track: bonus
kind: live_api
provider: RapidAPI (Twitter)
requires_env: [RAPIDAPI_KEY]
inputs: [country, limit]
outputs: [items]
side_effect: false
---
# trending

Gets currently trending topics on Twitter/X for a given country.
Reuses the same RapidAPI Twitter key as timeline and social_search.
