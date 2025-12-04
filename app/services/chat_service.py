from typing import List
from datetime import datetime  # only needed if you later timestamp messages
 
from ..storage.memory_store import MEMORY_STORE, Chat, Message
from ..utils.ids import new_id  # NOTE: not used anymore; you can remove it if unused
 
 
# Create a chat using MEMORY_STORE's async method
async def create_chat(provider: str, model: str, agent_id: str, title: str | None = None) -> Chat:
    # MEMORY_STORE.create_chat generates its own UUID for id
    chat = await MEMORY_STORE.create_chat(
        title=title or "",     # Chat.title is required in your dataclass
        provider=provider,
        model=model,
        agent_id=agent_id,
    )
    return chat
 
 
# Get a chat synchronously using MEMORY_STORE.get_chat
def get_chat(chat_id: str) -> Chat:
    return MEMORY_STORE.get_chat(chat_id)
 
 
# Add a message using MEMORY_STORE's async add_message
async def add_message_by_id(chat_id: str, role: str, content: str) -> Message:
    # role must be "user" | "assistant" | "system"
    msg = await MEMORY_STORE.add_message(chat_id=chat_id, role=role, content=content)
    return msg
 
 
# If you already have a Chat object and just want history:
def get_history(chat: Chat) -> List[Message]:
    return chat.messages