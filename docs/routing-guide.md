# Routing guide

## Decision sequence

1. Can GPT-6 Astra complete and verify the task safely in one thread? Use `ASTRA_LOCAL`.
2. Are there at least two independent, disjoint, separately verifiable packets? Use `ASTRA_DISPATCH` and assign each packet to a specialist.
3. Keep unresolved high-impact decisions in the Astra primary thread. Send high-stakes professional execution to `sol_worker`.

## Difficulty is not size

A thousand mechanical edits can be large but easy. A ten-line authorization change can be small but difficult. Dispatch based on published model strengths, uncertainty, blast radius, and error cost—not file count.

## Examples

### ASTRA_LOCAL

Add tests for established parser behavior and run the targeted suite.

### ASTRA_DISPATCH

Implement an approved feature whose UI, serializer, tests, and docs live in disjoint files:

- Fast UI implementation → `grok_worker` (preferred for speed)
- SEOGEO / Chinese article / human-like copy → `gemini_flash_worker`
- Routine tests → `luna_worker` (`gpt-6-luna`)
- Live API/docs check → `grok_worker`
- Auth cache policy implementation → `sol_worker`

Assign one writable owner per packet; Astra integrates and validates.

### Category examples

- Rename a symbol across 40 files → a codemod script, not a worker.
- Summarize 200 log lines into error classes → `luna_worker`, effort `low`.
- Fix a flaky test that fails only under concurrency → `sol_worker`; review by `grok_worker`.
- Add a settings page from an approved spec → `grok_worker`; review by `sol_worker` if it touches auth, otherwise Astra.
- Check what changed in a library released last month → `grok_worker`, with cited sources.
- Read a 90-page PDF with diagrams and extract requirements → `gemini_flash_worker`.
- Click through a signup flow in the browser → `sol_worker`, with an action log; Astra reviews the visible end state.
- Payments webhook change → `sol_worker` implements inside Astra's constraints; Astra reviews the diff and a second model checks it.

A packet that needs `luna_worker` at `high` or above is the wrong packet for it. Move it up one step (`luna_worker` → `grok_worker` → `sol_worker` → Astra).

## Astra dispatch shape

```text
Decision: split into independent packets and assign specialists.
Packets:
- sol_worker: <one high-stakes implementation or ruling>
- grok_worker effort=medium: <fast development or a live-docs check>
- luna_worker effort=low: <routine tests and mechanical edits; model gpt-6-luna>
- gemini_flash_worker effort=medium: <SEOGEO, Chinese article, human-like prose>
Constraints: disjoint writable files; one owner each.
Return: per-packet files changed, checks, remaining risks.
Astra: integrate, run final validation, accept or reject.
```

Do not ask any worker to “review everything” or “complete the whole feature.”
