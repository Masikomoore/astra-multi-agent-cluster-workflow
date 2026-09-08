# Changelog

## Unreleased

- GPT-6 Astra is the advisor and orchestrator (`ASTRA_LOCAL` / `ASTRA_DISPATCH`).
- Specialist workers: `sol_worker`; `grok_worker` preferred for fast development; `gemini_flash_worker` for SEOGEO and human-like Chinese writing; cheap daily mix of Luna and DeepSeek via `.codex/agents/cheap-daily.toml`; Qwen workers.
- Default cheap-daily mix is DeepSeek-V4-Flash (`luna = 0`, `deepseek = 10`); many relay gateways have blocked Luna. Concurrent thread cap: 8.
- Reasoning effort is hardcoded per agent file; Astra does not override it at dispatch.
- Calling examples use one swappable provider; sample `base_url` is xclis.ai GPT-稳定.
