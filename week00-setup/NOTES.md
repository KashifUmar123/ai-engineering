# Week 0 – First LLM calls

- Reasoning effort default vs minimal: 686 vs 168 tokens; minimal was cheaper but less accurate.
- System prompt asking for JSON changed the output format completely.
- Same prompt 3 times → 3 different answers. Lengths varied from X to Y tokens.
- Model ignored "3 sentences" instruction in most runs.

## 📅 Nov 12: Async & Parallel

- `asyncio.gather` = `Future.wait` → results in input order
- Python coroutines are **lazy** (nothing runs until awaited)
- Parallel time ≈ slowest call (14.4s → 3.6s)
- 1 failure kills `gather` → use `return_exceptions=True`
- `Semaphore(N)` = max N at once → avoids rate limits
- Concurrency limit ≠ batching (Batch API = grouped job, ~50% cheaper)
- 🔐 Never put API keys in a mobile app; one key + budget per project