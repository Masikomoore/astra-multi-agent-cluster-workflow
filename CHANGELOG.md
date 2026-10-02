# Changelog

## Unreleased

- README install links now point to the Masikomoore repository.
- README pitch: Astra as chief dispatcher so Plus is not limited to a few sentences; star if useful.
- README one-sentence Codex install: analyze this repo, then install it globally.
- `scripts/check-config.py` validates agent files, `[agents.*]` tables, effort values and the AGENTS.md effort table against the Codex model catalog, and flags project/global drift. Unnamed-subagent effort fallback is now `medium`. `sol_worker` gets `network_access = true` for browser/GUI packets (writes stay workspace-only).
- Task-category routing table in `AGENTS.md` (owner, never-assign, reviewer per category), cross-model review rule, escalation ladder, and a task-fit evidence section in `docs/models.md`.
- GPT-6 Astra is the advisor and orchestrator (`ASTRA_LOCAL` / `ASTRA_DISPATCH`).
- Specialist workers: `sol_worker` (`gpt-6.1-sol`); `grok_worker` (`grok-4.7`) preferred for fast development; `luna_worker` (`gpt-6-luna`) for cheap daily work; `gemini_flash_worker` (`gemini-3.8-flash`) for SEOGEO and human-like Chinese writing. DeepSeek, Qwen, and the cheap-daily mix file are removed. Concurrent thread cap: 8.
- Astra chooses reasoning effort per packet and clamps it to each model's allowed set. Worker TOML files no longer pin `model_reasoning_effort`.
- Calling examples use one swappable provider; sample `base_url` is xclis.ai GPT-稳定.
