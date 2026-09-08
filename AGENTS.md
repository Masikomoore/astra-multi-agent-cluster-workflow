# Astra multi-agent cluster rules

Use GPT-6 Astra as the primary advisor and orchestrator. Astra decomposes the user task and dispatches concurrent specialist workers.

OpenAI documents that Astra may delegate less often than a harness wants. In this workflow, parallel specialist dispatch is required whenever it would save time or improve quality.

## Automatic routing

Before substantial work, silently choose the cheapest route that preserves quality:

1. `ASTRA_LOCAL`: Astra handles the task in the primary thread when requirements are clear, risk is low or medium, and delegation overhead would exceed the work.
2. `ASTRA_DISPATCH`: Astra splits the work into at least two genuinely independent packets and assigns each packet to the specialist whose published strengths match the work.

Hard judgment stays in the Astra primary thread. High-stakes professional execution goes to `sol_worker`.

Infer the user's intent and carry authorized work to completion. Ask a focused question only when the answer would change the outcome. User instructions take precedence over this file when they conflict.

## Specialist assignment

Assign by task attributes, not by habit. If the needed model is unavailable, say so and use the next-best listed fallback.

| Agent | Model | Assign when |
| --- | --- | --- |
| `sol_worker` | `gpt-5.6-sol` | Architecture, security, science, compatibility, root-cause, or other high-stakes professional packets. |
| `grok_worker` | `grok-4.6` | Preferred for fast development. Also multimodal (text+image), live web/X search, current events. |
| `gemini_flash_worker` | `gemini-3.8-flash` | Multimodal and capable of fast development, but not the first pick for speed. Prefer this for SEOGEO, Chinese articles, and human-like prose. |
| `qwen_flash_worker` | `Qwen3.8-Flash-Next` | Cheap 1M-context coding/office work, especially Chinese-language packets that are not article/SEOGEO writing. |
| `qwen_uncensored_worker` | `qwen3.8-27b` | Reduced-refusal / special-instruction packets that aligned models decline. Huihui abliterated Qwen3.8-27B (Q4_K for local). |
| `luna_worker` | `gpt-5.6-luna` | Cheap daily execution pool (with DeepSeek). See mix below. |
| `deepseek_flash_worker` | `deepseek-v4-flash` | Cheap daily execution pool (with Luna). Close to Luna; concurrency may decide the mix. |

### Cheap daily mix

Routine, low-risk, disjoint packets that do not need Grok/Gemini/Sol/Qwen strengths go to the cheap daily pool.

Read `.codex/agents/cheap-daily.toml` before assigning those packets (if that file is missing, try `~/.codex/agents/cheap-daily.toml`). Do not spawn `cheap_daily`. `luna` and `deepseek` are weights per 10 assignments. Default is `0`/`10` (DeepSeek-V4-Flash only) because many relay gateways have blocked `gpt-5.6-luna`. Example `4` and `6` means 4 Luna, 6 DeepSeek out of 10. `10:0` is Luna only.

Keep a running count in the current session so the mix stays close to the ratio. If only one cheap packet is needed, sample with probability `luna / (luna + deepseek)`. Do not invent a third cheap model.

See [docs/models.md](docs/models.md) for published capabilities and [docs/providers.md](docs/providers.md) for provider parameters.

## Dispatch rules

Parallelize only when:

- packets do not depend on each other's unfinished output;
- every packet has explicit scope and acceptance criteria;
- writable files are disjoint;
- one owner is assigned per writable file;
- the primary Astra thread can integrate and validate the results.

If at any point work can be parallelized by delegating to another named agent, do so. Do not spawn agents for trivial tasks. More agents consume more tokens and can increase coordination cost.

Astra keeps high-impact unresolved decisions. Workers execute bounded packets; they do not redesign the system.

## Task packet

Every delegated packet must include objective, context, in-scope and out-of-scope files, constraints, acceptance criteria, exact validation, expected return, and escalation conditions.

Workers must stop on ambiguity, unexpected interface/dependency changes, security or data-integrity impact, unavailable validation, material scope expansion, or two failed attempts.

## Acceptance

The primary Astra thread owns integration and final acceptance. Inspect actual diffs and validation results; do not accept summaries alone. Workers never claim final acceptance.

Never claim a model ran unless the agent activity or tool result identifies it. If a configured model is unavailable, report the limitation and use the best available safe route.
