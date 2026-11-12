import asyncio
import time
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI()
sem = asyncio.Semaphore(2)  # 🅿️ max 2 at once

PROMPTS = [
    "Summarize the causes of WW1 in 1 sentence.",
    "Summarize the Cold War in 1 sentence.",
    "Who was Akbar the Great? 1 sentence.",
    "What was the Marshall Plan? 1 sentence.",
    "What was the Boston Tea Party? 1 sentence.",
]

async def ask(i: int, prompt: str) -> str:
    async with sem:
        print(f"▶️ start {i}  ({time.perf_counter() - T0:.1f}s)")
        r = await client.responses.create(
            model="gpt-5-mini",
            reasoning={"effort": "minimal"},
            input=prompt,
        )
        print(f"✅ done  {i}  ({time.perf_counter() - T0:.1f}s)")
        return r.output_text

async def main():
    global T0
    T0 = time.perf_counter()
    await asyncio.gather(*(ask(i, p) for i, p in enumerate(PROMPTS)))
    print(f"\nTotal: {time.perf_counter() - T0:.1f}s")

asyncio.run(main())