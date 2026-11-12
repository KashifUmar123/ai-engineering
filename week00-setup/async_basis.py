import asyncio
import time


async def fake_llm(name: str, delay: float) -> str:
    print(f"start {name}")
    await asyncio.sleep(delay)
    print(f"done {name}")
    return f"{name} result"

async def main() -> None:
    t = time.perf_counter()

    # fist example with sequential
    for n in ["A", "B", "C"]:
        await fake_llm(n, 1)

    print(f"Sequential elapsed: {time.perf_counter() - t}s\n")

    # example with parallel
    t = time.perf_counter()
    results = await asyncio.gather(
        fake_llm("A", 1),
        fake_llm("B", 1),
        fake_llm("C", 1)
    )

    print(results)
    print(f"Parallel elapsed: {time.perf_counter() - t}s")


asyncio.run(main())
