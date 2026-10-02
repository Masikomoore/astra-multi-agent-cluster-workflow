# Model roster

Facts below are from vendor docs checked on 2026-10-01. They describe published capabilities for routing. They are not runtime proof that Codex loaded the model. Provider parameters for the examples are in [providers.md](providers.md).

| Role | Agent | Model ID | Allowed effort (Astra clamps to this) |
| --- | --- | --- | --- |
| Advisor / orchestrator | primary thread | `gpt-6-astra` | `low` `medium` `high` `xhigh` `max` (no `none`) |
| Hard professional worker | `sol_worker` | `gpt-6.1-sol` | `low` `medium` `high` `xhigh` `max` (no `none`, no `minimal`) |
| Fast development (preferred) | `grok_worker` | `grok-4.7` | `low` `medium` `high` `xhigh` (`none` and `max` are not documented; not sent) |
| Cheap daily | `luna_worker` | `gpt-6-luna` | `low` `medium` `high` `xhigh` `max` (`none` is accepted by the vendor but never sent here) |
| Multimodal / SEOGEO / human-like Chinese writing | `gemini_flash_worker` | `gemini-3.8-flash` | `low` `medium` `high` |

Astra chooses effort per packet, then clamps to the allowed set above. Worker TOML files do not pin `model_reasoning_effort`. Primary session default is `xhigh`. Unnamed subagent fallback is `grok-4.7` at `high`. Dispatch rules: [AGENTS.md](../AGENTS.md).

Codex also applies a local catalog (`model_catalog_json`) that can set a smaller working context than the vendor maximum. Check it if a packet is near the limits below.

## gpt-6-astra

OpenAI's first GPT-6 model. Official description: most capable model, built for the hardest end-to-end work (computer use, browsing, software engineering, science, professional work). Supports multi-agent orchestration, async tool calling, and mid-turn steering.

- Context 1,050,000; max output 128,000; knowledge cutoff 2026-04-30
- Reasoning: `low` / `medium` / `high` / `xhigh` / `max` (`none` is unsupported)
- Price: $10 / $50 per 1M input/output; long prompts (>272k input) cost more
- Prompting: may delegate less than a harness wants; this repo requires dispatch when parallelism helps

Sources: [model page](https://developers.openai.com/api/docs/models/gpt-6-astra), [model guide](https://developers.openai.com/api/docs/guides/latest-model), [announcement](https://openai.com/index/gpt-6-astra/)

## gpt-6.1-sol

`sol_worker`. The high-stakes professional worker, not the advisor. Vendor description: near-Astra performance at lower cost for complex coding, computer use, and professional work.

- Context 1,050,000; max output 128,000; knowledge cutoff 2026-04-30
- Input text and image; output text
- Reasoning: `low` / `medium` (default) / `high` / `xhigh` / `max`. `none` and `minimal` are unsupported
- Price: $2 / $10 per 1M input/output ($0.10 cached input); prompts over 272k input are billed at 2x input and 1.5x output

Source: [model page](https://developers.openai.com/api/docs/models/gpt-6.1-sol)

## gpt-6-luna

`luna_worker`. The cheap daily worker.

- Context 1,050,000 (max input 922,000); max output 128,000; knowledge cutoff 2026-05-18
- Input text and image; output text
- Reasoning: `none` / `low` / `medium` (default) / `high` / `xhigh` / `max`. This pack never sends `none`
- Price: $0.10 / $0.50 per 1M input/output ($0.01 cached input); prompts over 272k are billed at 2x input and 1.5x output
- Supports function calling, web search, code interpreter, and computer use on the Responses API. The vendor notes that on Chat Completions, function calling only works with `reasoning_effort` set to `none`; Codex uses the Responses API

Source: [model page](https://developers.openai.com/api/docs/models/gpt-6-luna)

## gemini-3.8-flash

Google's most intelligent Flash model, GA around 2026-09-02. Multimodal and able to do fast development; in this workflow it is not the first pick for speed. Prefer it for SEOGEO, Chinese articles, and human-like prose.

- Inputs: text, image, audio, video. Context 1,048,576; max output 65,536
- Thinking: `low` / `medium` (default) / `high`. `minimal` errors
- Intro price through 2026-12-31: $0.75 / $3.75 per 1M

Sources: [Gemini API latest model](https://ai.google.dev/gemini-api/docs/latest-model), [Cloud model page](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash), [model card](https://deepmind.google/models/model-cards/gemini-3-8-flash/)

## grok-4.7

`grok_worker`. Preferred for speed, multimodal work, live web/X search, and current events. Also the unnamed-subagent fallback model.

- Context 500,000; no stated text output limit; knowledge cutoff May 2026
- Input text and image; output text
- Reasoning: `low` / `medium` / `high` (default) / `xhigh`. The docs do not list `none` or `max`, so neither is sent
- Price: $2 / $6 per 1M input/output below 200k prompt tokens (xAI pricing lists higher rates above that); `grok-4.7-fast` costs 2x
- Tools: function calling, web search, X search, code execution
- Responses API always returns `reasoning.encrypted_content`. xAI recommends setting `prompt_cache_key` for reliable cache hits

Sources: [xAI model page](https://docs.x.ai/developers/grok-4-7), [release notes](https://docs.x.ai/developers/release-notes)

## Task-fit evidence (as of 2026-10-01)

These notes back the routing table in [AGENTS.md](../AGENTS.md). Most come from third-party comparison sites and vendor-reported benchmarks, and the sources disagree on some numbers (for example, whether Astra or Sol leads on agentic coding). Treat the table as a starting heuristic and measure completion rate on your own packets before tightening it.

| Model | Reported fit | Reported weak spots |
| --- | --- | --- |
| `gpt-6-astra` | Strongest on computer use (OSWorld 2.0: 72.6 vs Sol 60.5 vs Luna 58.1); long engineering where errors cascade. GUI packets still go to `sol_worker` in this pack, with Astra reviewing the end state | Cost (about 5x Sol); rated "Critical" for cybersecurity, so it can refuse proof-of-concept exploit work |
| `gpt-6.1-sol` | Default for code changes, debugging, and report drafting; near-Astra on DeepSWE and Agents' Last Exam at about one-fifth the cost; fewer security restrictions than Astra | Unattended long-horizon runs |
| `gpt-6-luna` | Summarization, extraction, classification, tagging, high-volume work; only about 2 points behind Sol on DeepSWE (66.6 vs 68.8, both at max effort) | Long agentic chains where accuracy compounds; no published results on complex multi-part projects |
| `grok-4.7` | Agentic coding (Artificial Analysis Coding Agent Index 56, up from 47); about 188 tokens/s so multi-step loops finish sooner; hallucination rate 29% (down from 34%); live web/X search | Token-heavy at `xhigh`; community reports of weak frontend and 3D work (anecdotal); accuracy flat at 47% |
| `gemini-3.8-flash` | Multimodal (text, image, audio, video, PDF), 1M context, document-heavy workflows; vendor reports a strong DeepSWE result | Verbose at higher thinking levels; no parallel tool calls in the local catalog |

The Chinese-writing and SEOGEO assignment for `gemini_flash_worker` carries over from the earlier config. The sources above did not independently confirm it.

Role-split practice behind the "review by" column: one accountable orchestrator, bounded workers, and an independent verifier. A model should not be the only reviewer of its own change, and deterministic work goes to scripts.

Sources: [GPT-6 Sol vs Astra vs Luna](https://aitoolsreview.co.uk/insights/gpt-6-sol-vs-astra-vs-luna), [GPT-6.1 Sol vs GPT-6 Astra](https://aiagentstore.ai/ai-models/compare/gpt-6-1-sol-vs-gpt-6-astra), [Benchmarking Grok 4.7](https://artificialanalysis.ai/articles/benchmarking-grok-4-7), [Grok 4.7 review](https://www.stork.ai/blog/xais-grok-47-is-a-deceptive-upgrade), [Gemini 3.8 Flash review](https://blog.buildfastwithai.com/gemini-3-8-flash-review), [Multi-model coding agent stack](https://wavect.io/blog/multi-model-ai-coding-agent-stack-2026/)
