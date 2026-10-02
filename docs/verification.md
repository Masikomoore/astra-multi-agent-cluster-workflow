# Verification and fallbacks

## Drift check

```shell
python3 scripts/check-config.py
```

Compares project and `~/.codex` agent files, `[agents.*]` tables and effort values against the model catalog. Exits 1 on any mismatch.

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
}

assert config['model'] == 'gpt-6-astra'
assert config['model_reasoning_effort'] == 'xhigh'
assert config['agents']['default_subagent_model'] == 'grok-4.7'
assert config['agents']['default_subagent_reasoning_effort'] == 'medium'
assert config['agents']['max_concurrent_threads_per_session'] == 8

expected = {
    'sol-worker': ('sol_worker', 'gpt-6.1-sol'),
    'gemini-flash-worker': ('gemini_flash_worker', 'gemini-3.8-flash'),
    'grok-worker': ('grok_worker', 'grok-4.7'),
    'luna-worker': ('luna_worker', 'gpt-6-luna'),
}

assert set(agents) == set(expected)
for stem, (name, model) in expected.items():
    agent = agents[stem]
    assert agent['name'] == name, stem
    assert agent['model'] == model, stem
    assert 'model_reasoning_effort' not in agent, stem
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
2. Ask for two independent disjoint edits plus one live-docs check. Confirm Astra prefers `grok_worker` for fast development, `luna_worker` for routine tests, and `gemini_flash_worker` for SEOGEO/Chinese prose, writes a clamped reasoning effort on each packet, and that writable files have one owner.
3. Present a high-impact design question. Confirm Astra answers it in the primary thread (or sends implementation to `sol_worker` with a Sol-allowed effort), then Astra validates.
4. Spawn `gemini_flash_worker`. Confirm Gemini effort is only `low`/`medium`/`high`.

Static TOML validation cannot prove model access or runtime loading. Report actual model use only when Agent activity or tool output identifies it.

## Fallbacks

- If a configured model is missing from the provider catalog, report the gap. Use another listed worker only when its role still fits the packet.
- If GPT-6 Astra is unavailable, stop or explicitly document the substitute orchestrator.
- If custom agents are unavailable, select GPT-6 Astra as the main model and name specialists in the prompt.
- If parallelism adds more coordination than value, use `ASTRA_LOCAL`.
