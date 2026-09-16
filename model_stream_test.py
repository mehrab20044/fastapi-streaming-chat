import json
import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://togpt.ir/api/v1/chat/completions"
API_KEY = os.getenv("TOGPT_API_KEY")
MODEL = "gpt-5"

payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": "در یک جمله کوتاه راجب FastAPI توضیح بده.",
        }
    ],
    "stream": True,
}

start = time.perf_counter()

response = requests.post(
    API_URL,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json=payload,
    stream=True,
    timeout=60,
)

response.raise_for_status()

print("Status:", response.status_code)
print("Content-Type:", response.headers.get("content-type"))

for line in response.iter_lines(decode_unicode=True):
    if not line:
        continue

    print("RAW:", repr(line))

    if not line.startswith("data: "):
        continue

    data = line.removeprefix("data: ")

    if data == "[DONE]":
        break

    event = json.loads(data)

    chunk = event["choices"][0]["delta"].get("content")

    if chunk:
        elapsed = time.perf_counter() - start
        print("First direct chunk:", repr(chunk))
        print(f"Direct TTFC: {elapsed:.2f} seconds")
        break