# Astra multi-agent cluster workflow

[中文说明](README.md)

Let GPT-6 Astra act as the chief dispatcher and assign work to other models automatically, so Plus no longer dies after a few sentences. If this helps, come back and star the repo.

This repository is a **Codex configuration pack**, not an application.

GPT-6 Astra is the advisor and orchestrator. It splits work into disjoint packets and dispatches specialist workers in parallel.

Model-calling examples in this repo use the GPT-稳定 group on [xclis.ai](https://xclis.ai). Swap `base_url` and `env_key` for whatever provider you prefer.

Install in your own Codex with one sentence. Paste this prompt so Codex can analyze the project and install it globally:

```text
Analyze and learn this project, then install it globally in Codex: https://github.com/Masikomoore/astra-multi-agent-cluster-workflow
```

## What this project does

1. **Astra advises and accepts.** High-impact decisions stay in the primary thread. Workers execute bounded packets and never claim final acceptance.
2. **Dispatch by published strengths.** Prefer Grok 4.7 for fast development. Use Gemini 3.8 for multimodal SEOGEO and human-like Chinese writing. Use GPT-6.1 Sol for high-stakes professional work.
3. **Parallelism requires disjoint writable files.** One owner per file.
4. **Files on disk do not prove a model ran.** Report a model only when agent activity or a tool result identifies it.

Subagents still consume tokens and remain subject to account, model access, and concurrency limits.

## Architecture

```mermaid
flowchart TD
    U["User task"] --> A["GPT-6 Astra: classify and split"]
    A -->|clear, routine| E["ASTRA_LOCAL"]
    A -->|independent packets| P["ASTRA_DISPATCH"]
    P --> V["Astra integrates and validates"]
    E --> V
```

- `ASTRA_LOCAL`: one Astra thread is cheaper than delegation.
- `ASTRA_DISPATCH`: at least two independent, disjoint, separately verifiable packets.

High-impact decisions stay in the Astra primary thread. Send high-stakes implementation to `sol_worker`.

## Roster

All of these model IDs use the same provider in the examples.

| Role | Agent | Model ID |
| --- | --- | --- |
| Advisor / orchestrator | primary | `gpt-6-astra` |
| High-stakes professional work | `sol_worker` | `gpt-6.1-sol` |
| Fast development (preferred) | `grok_worker` | `grok-4.7` |
| Cheap daily | `luna_worker` | `gpt-6-luna` |
| Multimodal / SEOGEO / human-like Chinese writing | `gemini_flash_worker` | `gemini-3.8-flash` |

Grok 4.7 and Gemini 3.8 Flash are both multimodal and capable of fast development. **Prefer Grok 4.7 for speed.** Gemini also covers SEOGEO, Chinese articles, and human-like prose. `luna_worker` (`gpt-6-luna`) handles cheap daily work. Astra picks reasoning effort per packet and clamps it to what that model allows (see `AGENTS.md`).

See [docs/models.md](docs/models.md) for vendor capabilities.

## Provider example

User-level `~/.codex/config.toml` only. Project config cannot set `model_providers`. Codex requires `wire_api = "responses"`.

```toml
model = "gpt-6-astra"
model_reasoning_effort = "xhigh"
model_provider = "xclis_ai"

[model_providers.xclis_ai]
name = "xclis_ai"
base_url = "https://jp.xclis.ai/v1"
env_key = "API_KEY"
wire_api = "responses"
requires_openai_auth = false
supports_websockets = false
```

```bash
export API_KEY="sk-..."
API_KEY="$API_KEY" codex
```

Change only the `model` field to any ID in the roster. More replacement notes: [docs/providers.md](docs/providers.md).

## Install

One-sentence install in your own Codex:

```text
Analyze and learn this project, then install it globally in Codex: https://github.com/Masikomoore/astra-multi-agent-cluster-workflow
```

Or merge `.codex/config.toml`, `.codex/agents/*.toml`, and `AGENTS.md` into a project, then start a **new** Codex task.

A custom agent needs `name`, `description`, and `developer_instructions`. Copy agent files to `~/.codex/agents/` for personal use.

## License

[MIT](LICENSE)
