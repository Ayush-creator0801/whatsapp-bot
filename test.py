import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

CANDIDATES = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.8-flash",
]

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(timeout=15000),
)

print("Asking Google which models your key can use...")
try:
    available = {m.name.replace("models/", "") for m in client.models.list()}
    print(f"  {len(available)} models found.\n")
except Exception as e:
    print("  FAILED to list models:", e)
    available = set(CANDIDATES)

for model in CANDIDATES:
    if model not in available:
        print(f"{model}: not in your list, skipped")
        continue
    t = time.time()
    try:
        r = client.models.generate_content(
            model=model,
            contents="Say hello in five words.",
        )
        print(f"{model}: OK in {time.time() - t:.1f}s -> {r.text.strip()}")
    except Exception as e:
        msg = str(e).replace("\n", " ")[:110]
        print(f"{model}: FAILED after {time.time() - t:.1f}s -> {msg}")

print("\nDone.")