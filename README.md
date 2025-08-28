# Long-Term Memory Voice Agent (FastAPI + Vapi Custom LLM)

Build a production-ready voice agent backend that adds long-term memory to conversations and streams responses via an OpenAI-compatible Chat Completions API. Designed to plug into Vapi's Custom LLM feature.

## What this is
- FastAPI server exposing:
  - `POST /chat/completions` – OpenAI-style Chat Completions with server-sent events (SSE)
  - `GET /health` – health probe
- Memory via [`mem0`](https://mem0.ai/):
  - Searches for relevant memories and injects them into the system prompt
  - Stores new conversational snippets asynchronously
- Text generation via [Cerebras API](https://cerebras.ai/) using the OpenAI SDK
- Public exposure via `ngrok` for easy Vapi integration

## Requirements
- Python 3.10+
- A Cerebras API key
- (Optional) An ngrok account and auth token for stable public URLs

## Quickstart
```bash
# 1) Create and activate a virtual env (recommended)
python3 -m venv .venv && source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Set environment variables
# Required
export CEREBRAS_API_KEY="YOUR_CEREBRAS_API_KEY"
# Optional but recommended for stable ngrok URLs
# export NGROK_AUTHTOKEN="YOUR_NGROK_TOKEN"

# 4) Run the server
python main.py
```
You will see a line like:
```
Public URL: https://<random-subdomain>.ngrok.io
```

## API
- POST `/chat/completions`
  - Request body mirrors OpenAI Chat Completions. Minimal example:
  ```json
  {
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "model": "qwen-3-235b-a22b-instruct-2507",
    "stream": true,
    "max_tokens": 250,
    "temperature": 1.0,
    "top_p": 1.0
  }
  ```
  - Response is `text/event-stream` with SSE events. The first event is skipped internally to compute TTFT; subsequent events contain standard OpenAI-compatible chunks.

- GET `/health`
  - Returns `{ "status": "healthy", "timestamp": <unix-seconds> }`

## How memory works
- Before generation, the last few user/assistant turns are summarized into a query
- `mem0` is queried for related memories and appended to the system message as context
- All non-system messages are added to memory asynchronously after the response begins streaming

## Vapi integration (Custom LLM)
1. Start this server and note the ngrok public URL
2. In Vapi, create/update an Agent:
   - Provider: Custom LLM
   - URL: `https://<your-ngrok-domain>/chat/completions`
   - Method: POST
   - Streaming: SSE
   - Body: forward the OpenAI-style `messages` array (Vapi also sends caller info; this server will map `customer.number` when present to a deterministic `user_id` for memory)
3. Test a call; you should see streaming text and memory improving over time

## Environment variables
- `CEREBRAS_API_KEY` (required): API key for Cerebras
- `NGROK_AUTHTOKEN` (optional): if set, ngrok uses your account for stable domains
- `MEM0_*` (optional): if you use hosted Mem0, set the variables required by `mem0ai`

## Development notes
- Default model: `qwen-3-235b-a22b-instruct-2507` (change in `main.py`)
- Logs include TTFT once the first token arrives
- CORS is wide-open for ease of prototyping; tighten for production

## License
MIT

---
Pushed repository: [HugoPodworski/long-term-memory](https://github.com/HugoPodworski/long-term-memory)
