from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI()

SYSTEM = "You are a friendly, concise assistant."
CHAT_FILE = Path("week00-setup/chat.json")


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class Chat(BaseModel):
    messages: list[Message] = []


# 📂 load previous chat if it exists
if CHAT_FILE.exists():
    chat = Chat.model_validate_json(CHAT_FILE.read_text())
    print(f"(Loaded {len(chat.messages)} previous messages)")
else:
    chat = Chat()

while True:
    user = input("\nYou: ")
    if user.strip().lower() == "exit":
        break
    chat.messages.append(Message(role="user", content=user))

    stream = client.responses.create(
        model="gpt-5-mini",
        reasoning={"effort": "minimal"},
        instructions=SYSTEM,
        input=[m.model_dump() for m in chat.messages],
        stream=True,
    )

    print("AI: ", end="", flush=True)
    reply = ""
    usage = None
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
            reply += event.delta
        elif event.type == "response.completed":
            usage = event.response.usage

    chat.messages.append(Message(role="assistant", content=reply))

    # 💾 save after every turn (survives crashes / Ctrl+C, not just "exit")
    CHAT_FILE.write_text(chat.model_dump_json(indent=2))

    if usage:
        print(f"\n[input tokens: {usage.input_tokens} | output: {usage.output_tokens}]")