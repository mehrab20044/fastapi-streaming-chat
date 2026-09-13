# FastAPI Streaming Chat

پروژه آموزشی Week 5 از AI Backend Playbook.

## Progress

- Day 16 ✅ SSE and StreamingResponse
- Day 17 ⏳ LLM Streaming
- Day 18 ⏳ Redis and Cache
- Day 19 ⏳ Benchmarking
- Day 20 ⏳ Context Management

## Day 16

پیاده‌سازی Streaming در FastAPI با:

- `StreamingResponse`
- Async Generator و `yield`
- Server-Sent Events (SSE)
- `POST /chat`
- `text/event-stream`
- Client disconnect handling
- `asyncio.CancelledError`

## Run

```bash
source venv/bin/activate
uvicorn main:app --reload
