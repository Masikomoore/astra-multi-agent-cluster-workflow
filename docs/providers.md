# Provider wiring

The sample `base_url` below is `https://jp.xclis.ai/v1`. Replace `base_url` and `env_key` if you use another gateway.

Project `.codex/config.toml` cannot define `model_providers`. Put the provider in `~/.codex/config.toml`. Do not reuse reserved ids `openai`, `ollama`, or `lmstudio`. Codex only accepts `wire_api = "responses"`.

```toml
# ~/.codex/config.toml
model = "gpt-6-astra"
model_reasoning_effort = "high"
model_provider = "example"

[model_providers.example]
name = "example"
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

The same provider can call every worker model in this pack:

```text
gpt-6-astra
gpt-5.6-sol
gpt-5.6-luna
deepseek-v4-flash
gemini-3.8-flash
grok-4.6
Qwen3.8-Flash-Next
qwen3.8-27b
```

```bash
curl "${EXAMPLE_BASE_URL:-https://jp.xclis.ai/v1}/responses" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-6-astra","input":"Classify this task: ASTRA_LOCAL or ASTRA_DISPATCH?"}'
```

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url=os.environ.get("EXAMPLE_BASE_URL", "https://jp.xclis.ai/v1"),
)
print(client.models.list())
```

If a listed model is missing from `GET /v1/models`, say so and fall back to `luna_worker` or `sol_worker`. Never claim a specialist ran.

Optional local quant for `qwen3.8-27b`: serve Huihui Q4_K GGUF as an OpenAI-compatible server and point `base_url` at it. Ollama: `ollama run huihui_ai/Qwen3.8-abliterated`.
