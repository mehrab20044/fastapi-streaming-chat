import asyncio

from fastapi import FastAPI,Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "fastapi-streaming-chat is running"}


async def fake_stream():
    chunks = ["سلام ", "مهراب، ", "این ", "یک ", "stream ", "است."]

    for chunk in chunks:
        yield chunk
        await asyncio.sleep(1)


@app.get("/stream")
async def stream():
    return StreamingResponse(
        fake_stream(),
        media_type="text/plain",
    )
async def fake_sse_stream(request: Request, message: str):
    chunks = [
        "پیام شما: ",
        message,
        " | ",
        "پاسخ آزمایشی ",
        "به صورت streaming",
    ]

    try:
        for chunk in chunks:
            if await request.is_disconnected():
                print("Client disconnected.")
                break

            yield f"data: {chunk}\n\n"
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        print("Stream cancelled.")
        raise

    finally:
        print("Stream closed.")

@app.post("/chat")
async def chat (chat_request: ChatRequest,request: Request):
    return StreamingResponse(
        fake_sse_stream(request,chat_request.message),
        media_type="text/event-stream",
    )