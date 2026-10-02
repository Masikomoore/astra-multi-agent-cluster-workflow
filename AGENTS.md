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
| `sol_worker` | `gpt-6.1-sol` | Architecture, security, science, compatibility, root-cause, or other high-stakes professional packets. |
| `grok_worker` | `grok-4.7` | Preferred for fast development. Also multimodal (text+image), live web/X search, current events. |
| `luna_worker` | `gpt-6-luna` | Cheap daily execution: routine implementation, tests, exploration, and documentation. |
| `gemini_flash_worker` | `gemini-3.8-flash` | Multimodal and capable of fast development, but not the first pick for speed. Prefer this for SEOGEO, Chinese articles, and human-like prose. |

There is no cheap-daily mix and no Qwen or DeepSeek worker. Routine packets go to `luna_worker`. Fast development goes to `grok_worker`. Writing goes to `gemini_flash_worker`. Do not spawn `deepseek_flash_worker`, `qwen_flash_worker`, `qwen_uncensored_worker`, or `cheap_daily`.

## Task-category routing

Classify each packet into one category, then use that row. "Never" means do not assign even if the worker could do it; escalate instead.

| Category | Owner | Never | Review by |
| --- | --- | --- | --- |
| Architecture, root cause, high-impact decisions | Astra (primary) | any worker decides alone | Astra |
| Security, auth, crypto, payments, destructive migration, data integrity | `sol_worker` implements within Astra's constraints | `luna_worker`; `gemini_flash_worker` | Astra, plus a different-model check when the diff is non-trivial |
| Non-trivial debugging or cross-module change | `sol_worker` | `luna_worker` | `grok_worker` or Astra |
| Bounded feature work with a clear spec; rapid iteration loops | `grok_worker` | long unattended chains at `xhigh` | `sol_worker` for risky diffs, otherwise Astra |
| Live facts: web/X search, current events, post-cutoff docs | `grok_worker` (must cite sources) | other workers answering from memory | Astra spot-checks sources |
| Routine, high-volume, low-risk: tests for known behavior, mechanical edits, summaries, extraction, classification, log triage, docs | `luna_worker` | multi-step work where an early mistake compounds; anything that needs `high` or above | `grok_worker` or Astra |
| Audio, video, PDF, or corpus larger than ~450k tokens | `gemini_flash_worker` | the others (grok-4.7 takes text+image only, ~450k working context) | Astra |
| Chinese articles, SEOGEO, human-like prose | `gemini_flash_worker` | `luna_worker` for final copy | Astra |
| Screenshot or image reading | `grok_worker` or `gemini_flash_worker` | text-only routes | Astra |
| Browser, desktop, GUI, or form-filling automation | `sol_worker` | `luna_worker`; `grok_worker`; `gemini_flash_worker` | Astra, with visible state and action logs |
| Formatting, linting, codemods, other deterministic work | a script, not a model | all workers | the script's exit code |

Rules that cut across categories:

- The reviewer must not be the same model as the implementer. Pick the reviewer from the table, not from whichever agent is idle.
- Escalate one step on two failed attempts: `luna_worker` → `grok_worker` → `sol_worker` → Astra.
- Anything that publishes, pays, deletes, or messages externally stays in Astra, regardless of category.
- If a packet fits two rows, take the higher-risk row.

See [docs/models.md](docs/models.md) for published capabilities and the evidence behind this table, and [docs/providers.md](docs/providers.md) for provider parameters.

## Reasoning effort

Astra **chooses effort per packet**, then clamps it to what that model actually accepts. Worker TOML files do not set `model_reasoning_effort`, so Codex can apply the spawn value. If the spawn tool has an effort field, set it. Always write the chosen value into the task packet. If spawn cannot pass effort, Codex falls back to `default_subagent_reasoning_effort` (`high`); still record the intended value in the packet.

Never send an unsupported value (many gateways return HTTP 400). Pick a task level, then clamp:

| Agent | Model | Allowed `model_reasoning_effort` | Do not send | If unsure |
| --- | --- | --- | --- | --- |
| primary | `gpt-6-astra` | `low`, `medium`, `high`, `xhigh`, `max` | `none` | keep session `xhigh` |
| `sol_worker` | `gpt-6.1-sol` | `low`, `medium`, `high`, `xhigh`, `max` | `none`, `minimal` | `medium` (vendor default) |
| `grok_worker` | `grok-4.7` | `low`, `medium`, `high`, `xhigh` | `none`, `max` | fast dev: `medium` |
| `luna_worker` | `gpt-6-luna` | `low`, `medium`, `high`, `xhigh`, `max` | `none` | cheap daily: `low` |
| `gemini_flash_worker` | `gemini-3.8-flash` | `low`, `medium`, `high` | `none`, `minimal`, `xhigh`, `max` | writing: `medium` |

Clamps follow the vendor model pages (see [docs/models.md](docs/models.md)). `grok-4.7` documents only `low`–`xhigh`, so `none` and `max` are not sent. `gpt-6-luna` also accepts `none`, but this workflow never sends it. If a gateway returns HTTP 400 for effort, drop one allowed step and say so.

Task heuristic before clamp:

1. Cheap daily / mechanical edits (`luna_worker`) → `low`; bump to `medium` if the packet is not trivial. If it seems to need `high`, the packet belongs to another worker.
2. Fast development (`grok_worker`) → `medium`; bump to `high` if the packet is non-trivial; `xhigh` only after a failed attempt (it is token-heavy: one benchmark measured about 81k output tokens per task at `xhigh`).
3. SEOGEO / Chinese / human-like writing (Gemini) → `medium`; `high` for long or high-stakes copy.
4. Sol high-stakes → `high`; `xhigh` or `max` for architecture, security, or two failed attempts.
5. After two evidence-based failures, bump one allowed step if the model has a higher level.

Unnamed subagent fallback model is `grok-4.7`. Unnamed effort stays `high` unless Astra names a specialist.

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

Every delegated packet must include objective, assigned agent, **reasoning effort** (already clamped), context, in-scope and out-of-scope files, constraints, acceptance criteria, exact validation, expected return, and escalation conditions.

Workers must stop on ambiguity, unexpected interface/dependency changes, security or data-integrity impact, unavailable validation, material scope expansion, or two failed attempts.

## Acceptance

The primary Astra thread owns integration and final acceptance. Inspect actual diffs and validation results; do not accept summaries alone. Workers never claim final acceptance.

Never claim a model ran unless the agent activity or tool result identifies it. If a configured model is unavailable, report the limitation and use the best available safe route.
