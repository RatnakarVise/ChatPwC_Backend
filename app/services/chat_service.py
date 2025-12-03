from datetime import datetime
from typing import List
from ..storage.memory_store import MEMORY_STORE, Chat, Message
from ..utils.ids import new_id


def create_chat(provider: str, model: str, agent_id: str, title: str | None = None) -> Chat:
    chat_id = new_id("chat")
    chat = Chat(
        id=chat_id,
        provider=provider,
        model=model,
        agent_id=agent_id,
        title=title,
    )
    MEMORY_STORE[chat_id] = chat
    return chat


def get_chat(chat_id: str) -> Chat:
    chat = MEMORY_STORE.get(chat_id)
    if not chat:
        raise KeyError(f"Chat {chat_id} not found")
    return chat


def add_message(chat: Chat, role: str, content: str) -> None:
    chat.messages.append(
        Message(role=role, content=content, timestamp=datetime.utcnow())
    )


def get_history(chat: Chat) -> List[Message]:
    return chat.messages
