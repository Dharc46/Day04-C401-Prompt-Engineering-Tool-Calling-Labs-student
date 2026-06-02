---
name: translate
track: bonus
kind: live_api
provider: MyMemory
requires_env: []
inputs: [text, source_lang, target_lang]
outputs: [translated, match_quality, alternatives]
side_effect: false
---
# translate

Translates text between languages using the MyMemory Translation API.
Free tier, no API key required. Default translates English to Vietnamese.
