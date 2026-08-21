import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("LLM_MODEL")
base_url = os.getenv("LLM_BASE_URL")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to your environment or .env file.")
if not model:
    raise RuntimeError("LLM_MODEL is missing. Add it to your environment or .env file.")

if api_key.startswith("sk-or-v1-"):
    if not base_url or "openrouter.ai" not in base_url:
        base_url = "https://openrouter.ai/api/v1"
    if "/" not in model:
        model = f"openai/{model}"

client = OpenAI(api_key=api_key, base_url=base_url or None)

completion = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": "Hello"}
    ],
)

answer = completion.choices[0].message.content
print(answer)