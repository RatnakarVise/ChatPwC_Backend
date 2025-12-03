from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Literal

MessageRole = Literal["user", "assistant", "system"]


@dataclass
class ChatMessage:
    role: MessageRole
    content: str
    timestamp: datetime


@dataclass
class ChatSession:
    id: str
    provider: str
    model: str
    agent_id: str
    title: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    messages: List[ChatMessage] = field(default_factory=list)


@dataclass
class Job:
    id: str
    chat_id: str
    prompt: str
    status: Literal["queued", "running", "completed", "failed"] = "queued"
    result_message: Optional[str] = None
    output_docx_path: Optional[str] = None
    error: Optional[str] = None


# Simple in-memory stores
CHAT_STORE: Dict[str, ChatSession] = {}
JOB_STORE: Dict[str, Job] = {}
