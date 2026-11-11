from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()
client = OpenAI()

MODEL = "gpt-5-mini"
SYSTEM = "You are a friendly, concise assistant."
CHAT_FILE = Path("week00-setup/chat_v2.json")

KEEP_RECENT = 6   # always sent raw
CHUNK = 10        # summarize in blocks of 10


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class Chat(BaseModel):
    messages: list[Message] = []   # full history (never deleted)
    summary: str = ""              # compressed older messages
    summarized_upto: int = 0       # cursor: messages before this are in summary


def summarize(old_summary: str, msgs: list[Message]) -> str:
    convo = "\n".join(f"{m.role}: {m.content}" for m in msgs)
    resp = client.responses.create(
        model=MODEL,
        reasoning={"effort": "minimal"},
        instructions=(
            "Update the conversation summary. Keep key facts: names, preferences, "
            "decisions, open questions. Max 150 words. Output only the summary."
        ),
        input=f"<current_summary>\n{old_summary or 'None'}\n</current_summary>\n\n"
              f"<new_messages>\n{convo}\n</new_messages>",
    )
    return resp.output_text


def maybe_summarize(chat: Chat) -> None:
    raw_count = len(chat.messages) - chat.summarized_upto
    if raw_count >= KEEP_RECENT + CHUNK:
        end = chat.summarized_upto + CHUNK
        chunk = chat.messages[chat.summarized_upto:end]
        chat.summary = summarize(chat.summary, chunk)
        chat.summarized_upto = end
        print(f"\n📝 [summarized messages up to #{end}]")


def build_instructions(chat: Chat) -> str:
    if not chat.summary:
        return SYSTEM
    return f"{SYSTEM}\n\n<earlier_conversation_summary>\n{chat.summary}\n</earlier_conversation_summary>"


def build_input(chat: Chat) -> list[dict]:
    recent = chat.messages[chat.summarized_upto:]
    return [m.model_dump() for m in recent]


# 📂 load
chat = Chat.model_validate_json(CHAT_FILE.read_text()) if CHAT_FILE.exists() else Chat()
print(f"(Loaded {len(chat.messages)} messages, {chat.summarized_upto} summarized)")

while True:
    user = input("\nYou: ")
    if user.strip().lower() == "exit":
        break
    chat.messages.append(Message(role="user", content=user))

    stream = client.responses.create(
        model=MODEL,
        reasoning={"effort": "minimal"},
        instructions=build_instructions(chat),
        input=build_input(chat),
        stream=True,
    )

    print("AI: ", end="", flush=True)
    reply, usage = "", None
    for event in stream:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
            reply += event.delta
        elif event.type == "response.completed":
            usage = event.response.usage

    chat.messages.append(Message(role="assistant", content=reply))
    maybe_summarize(chat)                                # ⏱️ after the reply
    CHAT_FILE.write_text(chat.model_dump_json(indent=2))  # 💾 save

    raw = len(chat.messages) - chat.summarized_upto
    if usage:
        print(f"\n[input tokens: {usage.input_tokens} | raw msgs: {raw}]")