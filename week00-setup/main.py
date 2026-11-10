from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()

for i in range(3):
    resp = client.responses.create(
        model="gpt-5-mini",
        reasoning={"effort": "minimal"},
        instructions="Answer only in valid JSON with keys: summary, analogy. No other text.",
        input="Explain RAG to a Flutter developer in 3 sentences.",
    )
    print(f"\n=== Run {i+1} ===")
    print(resp.output_text)
    print("Output tokens:", resp.usage.output_tokens)