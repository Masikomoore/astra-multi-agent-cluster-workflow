# Provider wiring

GPT examples in this repository use the official Xclis **GPT-稳定（Stable）** group. Other workers need their own user-level providers.

Project `.codex/config.toml` cannot define `model_providers`. Codex ignores those keys in project config. Put providers in `~/.codex/config.toml`.

## Xclis GPT-稳定（this repo’s GPT path）

Official sources:

- Codex: [https://xclis.ai/docs/codex](https://xclis.ai/docs/codex)
- API: [https://xclis.ai/docs](https://xclis.ai/docs)
- Groups and prices: [https://xclis.ai/pricing](https://xclis.ai/pricing)

| Group | What Xclis says | Use for this workflow? |
| --- | --- | --- |
| **GPT-稳定（Stable）** | PRO channel for Codex and the Codex app; consistent supply. About ×0.036 of official prices. | **Yes. All GPT examples here.** |
| GPT-企业（Company） | Same base as 稳定, plus higher concurrency / multi-client. About ×0.5. | Optional upgrade, not the documented example. |
| GPT-特惠（Special Offers） | Third-party / self-subscription Plus pool; supply can drop. About ×0.017. | No. Do not use for these examples. |

The group is bound to the API key in the dashboard. Requests still send official model IDs:

| Workflow role | `model` |
| --- | --- |
| Advisor / orchestrator | `gpt-6-astra` |
| High-stakes worker | `gpt-5.6-sol` |
| Cheap fallback worker | `gpt-5.6-luna` |

Hosts:

| Role | Base URL |
| --- | --- |
| Official Codex docs | `https://jp.xclis.ai/v1` |
| Global | `https://us.xclis.ai/v1` |

### Codex

```toml
# ~/.codex/config.toml
model = "gpt-6-astra"
model_reasoning_effort = "high"
model_provider = "xclis"

[model_providers.xclis]
name = "Xclis GPT-稳定"
base_url = "https://jp.xclis.ai/v1"
env_key = "XCLIS_API_KEY"
wire_api = "responses"
requires_openai_auth = false
supports_websockets = false
```

```bash
export XCLIS_API_KEY="sk-..."   # dashboard key created in GPT-稳定
XCLIS_API_KEY="$XCLIS_API_KEY" codex
```

Do not reuse reserved provider ids `openai`, `ollama`, or `lmstudio`. Codex only accepts `wire_api = "responses"`.

### Responses (same wire as Codex)

```bash
curl https://jp.xclis.ai/v1/responses \
  -H "Authorization: Bearer $XCLIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-6-astra","input":"Classify this task: ASTRA_LOCAL or ASTRA_DISPATCH?"}'
```

### Chat Completions (OpenAI compatible)

```bash
curl https://jp.xclis.ai/v1/chat/completions \
  -H "Authorization: Bearer $XCLIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-5.6-luna","messages":[{"role":"user","content":"List files you would touch for a parser test-only change."}]}'
```

```python
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["XCLIS_API_KEY"], base_url="https://jp.xclis.ai/v1")
print(client.models.list())
```

If `GET /v1/models` does not list `gpt-6-astra` / `gpt-5.6-sol` / `gpt-5.6-luna`, the key is not on GPT-稳定 (or the group catalog changed). Recreate the key in that group; do not invent a prefixed model id.

## Non-GPT workers (optional)

These are not GPT-稳定. Wire them only if you actually have access.

```toml
# ~/.codex/config.toml  — extra providers, still user-level

[model_providers.deepseek]
name = "DeepSeek"
base_url = "https://api.deepseek.com/v1"
env_key = "DEEPSEEK_API_KEY"
wire_api = "responses"

[model_providers.gemini]
name = "Gemini"
base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
env_key = "GEMINI_API_KEY"
wire_api = "responses"

[model_providers.xai]
name = "xAI"
base_url = "https://api.x.ai/v1"
env_key = "XAI_API_KEY"
wire_api = "responses"

[model_providers.qwen]
name = "Qwen"
base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
env_key = "DASHSCOPE_API_KEY"
wire_api = "responses"

[model_providers.local_qwen27b]
name = "Huihui Qwen3.8-27B"
base_url = "http://127.0.0.1:8080/v1"
env_key = "LOCAL_QWEN27B_API_KEY"
wire_api = "responses"
```

If a vendor is Chat Completions-only, put a Responses translator in front. Missing specialists fall back to `luna_worker` or `sol_worker` on GPT-稳定. Never claim a specialist ran.

## Local Huihui Q4_K

1. Download `Huihui-Qwen3.8-27B-abliterated-Q4_K` from [huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF](https://huggingface.co/huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF).
2. Serve it as an OpenAI-compatible server.
3. Map Codex model id `qwen3.8-27b` to that server.

Ollama: `ollama run huihui_ai/Qwen3.8-abliterated`.
