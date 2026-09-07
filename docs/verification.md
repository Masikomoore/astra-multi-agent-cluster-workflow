# Verification and fallbacks

## Static check

Run from the repository root:

```shell
python3 - <<'PY'
from pathlib import Path
import tomllib

root = Path('.codex')
config = tomllib.loads((root / 'config.toml').read_text())
agents = {
    path.stem: tomllib.loads(path.read_text())
    for path in sorted((root / 'agents').glob('*.toml'))
    if path.name != 'cheap-daily.toml'
}

assert config['model'] == 'gpt-6-astra'
assert config['model_reasoning_effort'] == 'xhigh'
assert config['agents']['default_subagent_model'] == 'gpt-5.6-luna'
assert config['agents']['default_subagent_reasoning_effort'] == 'max'
assert config['agents']['max_concurrent_threads_per_session'] == 8

cheap = tomllib.loads((root / 'agents' / 'cheap-daily.toml').read_text())
assert cheap['name'] == 'cheap_daily'
assert cheap['luna'] >= 0 and cheap['deepseek'] >= 0
assert cheap['luna'] + cheap['deepseek'] > 0

expected = {
    'luna-worker': ('luna_worker', 'gpt-5.6-luna', 'max'),
    'sol-worker': ('sol_worker', 'gpt-5.6-sol', 'high'),
    'deepseek-flash-worker': ('deepseek_flash_worker', 'deepseek-v4-flash', 'high'),
    'gemini-flash-worker': ('gemini_flash_worker', 'gemini-3.8-flash', 'high'),
    'grok-worker': ('grok_worker', 'grok-4.6', 'high'),
    'qwen-flash-next-worker': ('qwen_flash_worker', 'Qwen3.8-Flash-Next', 'high'),
    'qwen-uncensored-worker': ('qwen_uncensored_worker', 'qwen3.8-27b', 'medium'),
}

assert set(agents) == set(expected)
for stem, (name, model, effort) in expected.items():
    agent = agents[stem]
    assert agent['name'] == name, stem
    assert agent['model'] == model, stem
    assert agent['model_reasoning_effort'] == effort, stem
    assert agent['description'].strip()
    assert agent['developer_instructions'].strip()
    for key in ('name', 'description', 'developer_instructions'):
        assert key in agent
print('Static configuration checks passed.')
PY
```

## Runtime checks

Start a new task after installing the files.

1. Ask for one small bounded edit. Confirm the primary task identifies GPT-6 Astra.
2. Ask for two independent disjoint edits plus one live-docs check. Confirm Astra prefers `grok_worker` for fast development, uses `gemini_flash_worker` for SEOGEO/Chinese prose, mixes cheap daily from `.codex/agents/cheap-daily.toml`, and that writable files have one owner.
3. Present a high-impact design question. Confirm Astra answers it in the primary thread (or sends implementation to `sol_worker`), then Astra validates.

Static TOML validation cannot prove model access or runtime loading. Report actual model use only when Agent activity or tool output identifies it.

## Fallbacks

- If a configured model is missing from the provider catalog, report the gap and fall back through the cheap-daily mix, then `sol_worker`.
- If GPT-6 Astra is unavailable, stop or explicitly document the substitute orchestrator.
- If custom agents are unavailable, select GPT-6 Astra as the main model and name specialists in the prompt.
- If parallelism adds more coordination than value, use `ASTRA_LOCAL`.
