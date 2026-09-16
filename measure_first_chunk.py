import json
import time

import requests

start = time.perf_counter()

response = requests.post(
    "http://127.0.0.1:8000/chat",
    headers={"Content-Type": "application/json"},
    json={"message": "در یک جمله کوتاه FastAPI را توضیح بده."},
    stream=True,
    timeout=60,
)

response.raise_for_status()

for line in response.iter_lines(decode_unicode=True):
    if not line or not line.startswith("data: "):
        continue

    data = json.loads(line.removeprefix("data: "))

    if data.get("content"):
        elapsed = time.perf_counter() - start
        print("First chunk: ", repr(data["content"]))
        print(f"Time to first chunk: {elapsed:.2f} seconds")
        break
