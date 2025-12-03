from datetime import datetime
from typing import List
from ..storage.memory_store import CHAT_STORE, ChatSession, ChatMessage
from ..utils.ids import new_id


def create_chat(provider: str, model: str, agent_id: str, title: str | None = None) -> ChatSession:
    chat_id = new_id("chat")
    chat = ChatSession(
        id=chat_id,
        provider=provider,
        model=model,
        agent_id=agent_id,
        title=title,
    )
    CHAT_STORE[chat_id] = chat
    return chat


def get_chat(chat_id: str) -> ChatSession:
    chat = CHAT_STORE.get(chat_id)
    if not chat:
        raise KeyError(f"Chat {chat_id} not found")
    return chat


def add_message(chat: ChatSession, role: str, content: str) -> None:
    chat.messages.append(
        ChatMessage(role=role, content=content, timestamp=datetime.utcnow())
    )


def get_history(chat: ChatSession) -> List[ChatMessage]:
    return chat.messages
