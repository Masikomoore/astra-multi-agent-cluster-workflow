# Model roster

Facts below are from vendor docs and Hugging Face cards as of 2026-09-07. They describe published capabilities for routing. They are not runtime proof that Codex loaded the model. Provider parameters for the examples are in [providers.md](providers.md).

| Role | Agent | Model ID | Allowed effort (Astra clamps to this) |
| --- | --- | --- | --- |
| Advisor / orchestrator | primary thread | `gpt-6-astra` | `low` `medium` `high` `xhigh` `max` (no `none`) |
| Hard professional worker | `sol_worker` | `gpt-5.6-sol` | `none` `low` `medium` `high` `xhigh` `max` |
| Fast development (preferred) | `grok_worker` | `grok-4.6` | `low` `medium` `high` `xhigh` |
| Multimodal / SEOGEO / human-like Chinese writing | `gemini_flash_worker` | `gemini-3.8-flash` | `low` `medium` `high` |
| Cheap daily (mixed) | `deepseek_flash_worker` | `deepseek-v4-flash` | thinking `high` `max` |
| Cheap Chinese / office | `qwen_flash_worker` | `Qwen3.8-Flash-Next` | `low` `medium` `xhigh` |
| Reduced-refusal | `qwen_uncensored_worker` | `qwen3.8-27b` | `medium` `xhigh` |
| Cheap daily (mixed) | `luna_worker` | `gpt-5.6-luna` | `none` `low` `medium` `high` `xhigh` `max` |

Cheap daily mix is `.codex/agents/cheap-daily.toml` (`luna` : `deepseek` per 10 assignments). Default `0:10` (DeepSeek-V4-Flash) because many relay gateways have blocked Luna.

Astra chooses effort per packet, then clamps to the allowed set above. Worker TOML files do not pin `model_reasoning_effort`. Primary session default is `xhigh`. Unnamed subagent fallback is `high`. Dispatch rules: [AGENTS.md](../AGENTS.md).

## gpt-6-astra

OpenAI's first GPT-6 model. Official description: most capable model, built for the hardest end-to-end work (computer use, browsing, software engineering, science, professional work). Supports multi-agent orchestration, async tool calling, and mid-turn steering.

- Context 1,050,000; max output 128,000; knowledge cutoff 2026-04-30
- Reasoning: `low` / `medium` / `high` / `xhigh` / `max` (`none` is unsupported)
- Price: $10 / $50 per 1M input/output; long prompts (>272k input) cost more
- Prompting: may delegate less than a harness wants; this repo requires dispatch when parallelism helps

Sources: [model page](https://developers.openai.com/api/docs/models/gpt-6-astra), [model guide](https://developers.openai.com/api/docs/guides/latest-model), [announcement](https://openai.com/index/gpt-6-astra/)

## gpt-5.6-sol

GPT-5.6 flagship (`gpt-5.6` alias routes here). Complex professional work, coding, cybersecurity, science. In this workflow it is `sol_worker`, not the advisor.

- Context 1,050,000; max output 128,000; knowledge cutoff 2026-02-16
- Promotional price at least through 2026-11-21: $4 / $20 per 1M
- Native in Codex; use when Astra needs Sol-class execution without spending Astra tokens on the packet

Source: [model page](https://developers.openai.com/api/docs/models/gpt-5.6-sol)

## deepseek-v4-flash

DeepSeek-V4 Flash: 284B MoE / 13B active. Fast, efficient, economical. Reasoning approaches V4-Pro; simple agent tasks are similar; hardest agent work still favors Pro.

- 1M context; max output 384k; thinking and non-thinking; tools and JSON
- Cheap daily pool with Luna; mix via `.codex/agents/cheap-daily.toml`. Close to Luna; concurrency may decide the weights.

Sources: [V4 preview](https://api-docs.deepseek.com/news/news260424/), [pricing](https://api-docs.deepseek.com/quick_start/pricing), [HF weights](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash)

## gemini-3.8-flash

Google's most intelligent Flash model, GA around 2026-09-02. Multimodal and able to do fast development; in this workflow it is not the first pick for speed. Prefer it for SEOGEO, Chinese articles, and human-like prose.

- Inputs: text, image, audio, video. Context 1,048,576; max output 65,536
- Thinking: `low` / `medium` (default) / `high`. `minimal` errors
- Intro price through 2026-12-31: $0.75 / $3.75 per 1M

Sources: [Gemini API latest model](https://ai.google.dev/gemini-api/docs/latest-model), [Cloud model page](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash), [model card](https://deepmind.google/models/model-cards/gemini-3-8-flash/)

## grok-4.6

xAI frontier model for coding, agentic tasks, and knowledge work. Default in Grok Build. In this workflow it is the **preferred fast-development** worker; also multimodal (text+image).

- Context 500,000; text+image in, text out; knowledge cutoff 2026-02-01
- Reasoning: `low` / `medium` / `high` (default) / `xhigh`
- Price: $2 / $6 per 1M below 200k prompt tokens; double above that
- Tools: function calling, web search, X search, code execution

Sources: [Grok 4.6 docs](https://docs.x.ai/developers/grok-4-6), [release notes](https://x.ai/docs/release-notes), [announcement](https://x.ai/news/grok-4-6)

## Qwen3.8-Flash-Next

Open weights are `Qwen/Qwen3.8-Flash-Next` (Qwen4 architecture preview). This workflow uses catalog id `Qwen3.8-Flash-Next`.

- ~125B MoE + n-gram embeddings, ~6B active/token
- Strong coding/office; cheap long context; especially good for Chinese packets

Sources: [HF Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next), [百炼 qwen3.8-flash](https://help.aliyun.com/zh/model-studio/qwen3-8-flash)

## qwen3.8-27b (Huihui abliterated)

Base Qwen3.8-27B is a 27B dense vision-language model (Apache-2.0, 262k native context). This workflow uses the Huihui abliterated checkpoint so the worker can accept special instructions that aligned models refuse.

- Weights: [huihui-ai/Huihui-Qwen3.8-27B-abliterated](https://huggingface.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated)
- Local quant named by this repo's users: Q4_K GGUF under [huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF](https://huggingface.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF)
- Latest ablation: layers 18–51; MTP and vision unmodified
- Ollama: `huihui_ai/Qwen3.8-abliterated`
- Huihui card: crude proof-of-concept; reduced safety filtering; research/controlled use
- Reasoning effort in this workflow: `medium` or `xhigh` only

`qwen_uncensored_worker` still must not provide operational assistance for violent crime or child sexual exploitation.

## gpt-5.6-luna

Cheap daily pool with DeepSeek. Mix via `.codex/agents/cheap-daily.toml`. Also `default_subagent_model` when Codex needs a fallback spawn. Default mix is DeepSeek-only because many relay gateways have blocked Luna.
