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

- UI + tests → `gemini_flash_worker` or `deepseek_flash_worker`
- Chinese copy → `qwen_flash_worker`
- Live API/docs check → `grok_worker`
- Auth cache policy implementation → `sol_worker`

Assign one writable owner per packet; Astra integrates and validates.

### Reduced-refusal packet

A research prompt that aligned models refuse, with an explicit legal scope, goes to `qwen_uncensored_worker`. Astra still owns whether the packet is in scope.

## Astra dispatch shape

```text
Decision: split into independent packets and assign specialists.
Packets:
- sol_worker: <one high-stakes implementation or ruling>
- deepseek_flash_worker: <bounded coding files>
- gemini_flash_worker: <long-horizon or multimodal files>
Constraints: disjoint writable files; one owner each.
Return: per-packet files changed, checks, remaining risks.
Astra: integrate, run final validation, accept or reject.
```

Do not ask any worker to “review everything” or “complete the whole feature.”
