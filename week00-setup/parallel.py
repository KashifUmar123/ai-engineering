import asyncio
import time
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI()

PROMPTS = [
    "Summarize the causes of WW1 in 1 sentence.",
    "Summarize the Cold War in 1 sentence.",
    "Who was Akbar the Great? 1 sentence.",
    "What was the Marshall Plan? 1 sentence.",
    "What was the Boston Tea Party? 1 sentence.",
]

async def ask(prompt: str, model:str = "gpt-5-mini") -> str:
    r = await client.responses.create(
        model=model,
        reasoning={"effort": "minimal"},
        input=prompt,
    )
    return r.output_text

async def sequential() -> None:
    return [await ask(prompt) for prompt in PROMPTS]

async def parallel() -> None:
    tasks = [ask(p) for p in PROMPTS]
    tasks[2] = ask(PROMPTS[2], model="fake-model")  # 💥
    return await asyncio.gather(*tasks, return_exceptions = True)


async def main() -> None:
    for fn in (sequential, parallel):
        t = time.perf_counter()
        answers = await fn()
        t = time.perf_counter() - t
        print(f"{fn.__name__} took {t:.2f} seconds")
        for r in answers:
            if isinstance(r, Exception):
                print("❌", type(r).__name__)
            else:
                print("✅", r[:60])


asyncio.run(main())