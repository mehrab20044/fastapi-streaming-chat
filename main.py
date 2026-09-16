import asyncio
import json
import os 

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI,Request
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI()

load_dotenv()
API_URL = "https://togpt.ir/api/v1/chat/completions"
API_KEY = os.getenv("TOGPT_API_KEY")
MODEL = "gpt-5"

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
async def model_sse_stream(request: Request, message: str):
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer briefly in Persian.",
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        "stream": True,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                API_URL,
                headers=headers,
                json=payload,
            ) as response:

                response.raise_for_status()

                async for line in response.aiter_lines():

                    if await request.is_disconnected():
                        print("Client disconnected.")
                        break

                    if not line:
                        continue

                    if not line.startswith("data: "):
                        continue

                    data = line.removeprefix("data: ")

                    if data == "[DONE]":
                        break

                    event = json.loads(data)

                    choices = event.get("choices", [])

                    if not choices:
                        continue

                    delta = choices[0].get("delta", {})
                    chunk = delta.get("content")

                    if chunk:
                        output = json.dumps(
                            {"content": chunk},
                            ensure_ascii=False,
                        )

                        yield f"data: {output}\n\n"

    except asyncio.CancelledError:
        print("Stream cancelled.")
        raise

    except httpx.HTTPError as error:
        print(f"HTTP stream error: {error}")

        error_data = json.dumps(
            {"error": "Model API request failed."},
            ensure_ascii=False,
        )

        yield f"event: error\ndata: {error_data}\n\n"

    except json.JSONDecodeError as error:
        print(f"Invalid stream JSON: {error}")

        error_data = json.dumps(
            {"error": "Invalid data received from model."},
            ensure_ascii=False,
        )

        yield f"event: error\ndata: {error_data}\n\n"

    finally:
        print("Model stream closed.")

@app.post("/chat")
async def chat (chat_request: ChatRequest,request: Request):
    return StreamingResponse(
        model_sse_stream(request,chat_request.message),
        media_type="text/event-stream",
    )

@app.get("/ui")
async def ui():
    return FileResponse("index.html")