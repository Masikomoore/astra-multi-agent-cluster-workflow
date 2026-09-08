# Changelog

## Unreleased

- README pitch: Astra as chief dispatcher so Plus is not limited to a few sentences; star if useful.
- README one-sentence Codex install: analyze this repo, then install it globally.
- GPT-6 Astra is the advisor and orchestrator (`ASTRA_LOCAL` / `ASTRA_DISPATCH`).
- Specialist workers: `sol_worker`; `grok_worker` preferred for fast development; `gemini_flash_worker` for SEOGEO and human-like Chinese writing; cheap daily mix of Luna and DeepSeek via `.codex/agents/cheap-daily.toml`; Qwen workers.
- Default cheap-daily mix is DeepSeek-V4-Flash (`luna = 0`, `deepseek = 10`); many relay gateways have blocked Luna. Concurrent thread cap: 8.
- Astra chooses reasoning effort per packet and clamps it to each model's allowed set. Worker TOML files no longer pin `model_reasoning_effort`.
- Calling examples use one swappable provider; sample `base_url` is xclis.ai GPT-稳定.
