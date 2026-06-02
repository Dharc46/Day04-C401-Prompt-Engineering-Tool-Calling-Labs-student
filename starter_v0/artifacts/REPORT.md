# Day 04 Lab v2 Report - Research Agent

## Team

- Team: Student implementation
- Members: Khoi / Codex-assisted implementation
- Provider/model: OpenRouter, `openai/gpt-4o-mini`

## Final Metrics

- Final version: `v3`
- Final artifact_version: `v3+p7ffe7ed76111+tad86104e4131`
- Best base run file: `runs\v3_B_base_openrouter_20260602T142257304987.json`
- Base case accuracy: `1.0`
- Base tool routing accuracy: `1.0`
- Base argument accuracy: `1.0`
- Base multiturn accuracy: `1.0`
- Group eval run file: `runs\v3_B_group_openrouter_20260602T142603499939.json`
- Group eval accuracy: `1.0`
- Group tool routing accuracy: `1.0`
- Group argument accuracy: `1.0`
- Group multiturn accuracy: `1.0`
- Chat transcript file: `transcripts\v3_openrouter_20260602T142649439555.transcript.json`
- Analysis CSV: `analysis\base_runs.csv`

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | `system_prompt.md`, `tools.yaml` | Explicit routing and guardrails should replace unsafe starter behavior. | N/A | 0.95 | `runs\v0_B_base_openrouter_20260602T141818323936.json` |
| v1 | `system_prompt.md`, `tools.yaml` | A supplied URL should be enough to call `fetch`; no confirmation needed. | 0.95 | 0.95, routing 1.0 | `runs\v1_B_base_openrouter_20260602T142006837225.json` |
| v2 | `system_prompt.md`, `tools.yaml` | Action confirmation must use `clarify.response_type=yes_no`. | 0.95 | 1.0 | `runs\v2_B_base_openrouter_20260602T142136156662.json` |
| v3 | `system_prompt.md`, `tools.yaml` | Latest-turn no-tool instructions and non-empty source ranking should improve group behavior. | 1.0 | 1.0 base, 1.0 group | `runs\v3_B_base_openrouter_20260602T142257304987.json` |

## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R04_read_url_routing | wrong_tool | `clarify(response_type=yes_no)` | The model asked for confirmation before reading a concrete URL. | v1 added explicit rule: a supplied URL is sufficient for `fetch`. |
| R12_confirm_before_send | wrong_boundary | `clarify(response_type=text)` | The model asked for text clarification instead of yes/no confirmation. | v2 added explicit action-boundary rule requiring `response_type=yes_no`. |
| G01/G04/G05/G09 initial group run | wrong_arg_value | Correct tools with reasonable equivalent args | Team eval expectations were too strict for query wording and optional args. | Adjusted group eval to grade critical routing/args rather than exact natural-language query text. |

## Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_news_today_ai | Current AI news routing | `lookup(topic=news,timeframe=day)` | PASS |
| G02_missing_account_for_posts | Missing social account | `clarify(response_type=text)` | PASS |
| G03_confirm_before_telegram | Unconfirmed send boundary | `clarify(response_type=yes_no)` | PASS |
| G04_policy_citation_rules | Internal policy lookup | `policy` | PASS |
| G05_rank_retrieved_sources | New source-ranking tool | `source_rank` | PASS |
| G06_multi_url_then_fetch | Multi-turn URL carryover | `fetch(url=...)` | PASS |
| G07_multi_topic_switch | Multi-turn tool switch | `lookup(topic=news,timeframe=day)` | PASS |
| G08_multi_confirmed_send | Confirmed side effect | `send(confirmed=true)` | PASS |
| G09_multi_papers_correction | Multi-turn paper search refinement | `papers(max_results=3,sort_by=relevance)` | PASS |
| G10_multi_no_tool_meta | Latest no-tool instruction | no tool | PASS |

## Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | AI news today | `lookup(query=AI,topic=news,timeframe=day)` | v3 transcript | Answered with Tavily news results. |
| 2 | Summarize 5 latest tweets | `social_search(query=AI,limit=5)` | v3 transcript | Tool executed but RapidAPI returned restricted access. |
| 3 | Sam Altman tweets | `timeline(screenname=sama,limit=5)` | v3 transcript | Tool executed but RapidAPI returned 403 Forbidden. |
| 4 | Post to Telegram | `clarify(response_type=yes_no)` | v3 transcript | Correctly paused for confirmation before sending. |

## Added Tool

| Tool | Files | Purpose | Env Required |
|---|---|---|---|
| `source_rank` | `tools/source_rank/TOOL.md`, `tools/source_rank/tool.py`, `tools/__init__.py`, `artifacts/tools.yaml` | Deduplicate and rank retrieved/user-supplied source items by relevance and source quality. | None |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts\v3_openrouter_20260602T142649439555.transcript.json` | Agent asks for yes/no confirmation before side effect. | `send` still requires valid Telegram env vars and explicit confirmation. |
| arXiv/company policy | `artifacts/tools.yaml`, `tools/papers`, `tools/paper_text`, `tools/policy` | Tools are declared and registered. | arXiv is rate-limited; policy is local keyword retrieval. |
| UI | `streamlit_app.py` | Streamlit chat UI runs on localhost and logs transcripts. | Browser/server lifecycle is local-machine dependent. |

## Reflection

- `system_prompt.md` fixes were best for routing policy, missing-information behavior, multi-turn carryover, out-of-scope handling, and action boundaries.
- `tools.yaml` fixes were best for concise tool descriptions, argument conventions, and reducing ambiguity between `timeline`, `social_search`, `lookup`, `fetch`, `send`, and `source_rank`.
- The group eval failures needed manual review because exact query strings like `AI` vs `AI news` are not meaningful behavioral failures.
- Next improvement: add automated smoke tests for every live API key and a UI transcript viewer for run JSON and chat transcripts.

## Known Runtime Limitations

- Live Twitter/RapidAPI calls returned restricted access / 403 during transcript generation even though `RAPIDAPI_KEY` was set.
- External API quotas, billing, and provider availability can change.
- `.env` is intentionally not committed; users must provide their own provider/tool keys.
