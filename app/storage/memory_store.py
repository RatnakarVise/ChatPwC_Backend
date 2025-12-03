"""
memory_store.py
---------------
In-memory persistence layer for Chats, Messages, and Jobs.

This is NOT a database, it is temporary runtime storage.
Used until Redis / Postgres is plugged in.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal, Any
import asyncio
import uuid


# =======================
# Chat & Message Models
# =======================

@dataclass
class Message:
    role: Literal["user", "assistant", "system"]
    content: str


@dataclass
class Chat:
    id: str
    title: str
    provider: str          # ex: openai, anthropic etc.
    model: str             # ex: gpt-5, gpt-4o, claude 3 etc.
    agent_id: str          # Agent type: tsfs, abap, cds, form etc.
    messages: List[Message] = field(default_factory=list)


# =======================
# Job Model
# =======================

JobStatus = Literal["queued", "running", "completed", "failed"]


@dataclass
class Job:
    id: str
    chat_id: str
    prompt: str

    status: JobStatus = "queued"
    logs: List[str] = field(default_factory=list)
    result_message: Optional[str] = None

    # Optional: for downloadable generated DOCX/ZIP files
    output_docx_path: Optional[str] = None

    # Optional: preserve entire structured result (text, json, paths etc.)
    output_payload: Optional[Dict[str, Any]] = None

    error: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


# =======================
# Memory Store
# =======================

class MemoryStore:
    """
    Generic in-memory storage with concurrency locks.
    Replace with Redis/DB later.
    """

    def __init__(self) -> None:
        self.chats: Dict[str, Chat] = {}
        self.jobs: Dict[str, Job] = {}
        self._lock = asyncio.Lock()

    # ---------- Chat Methods ----------
    async def create_chat(self, title: str, provider: str, model: str, agent_id: str) -> Chat:
        async with self._lock:
            chat_id = str(uuid.uuid4())
            chat = Chat(id=chat_id, title=title, provider=provider, model=model, agent_id=agent_id)
            self.chats[chat_id] = chat
            return chat

    async def add_message(self, chat_id: str, role: Literal["user", "assistant", "system"], content: str) -> Message:
        async with self._lock:
            chat = self.chats.get(chat_id)
            if not chat:
                raise KeyError(f"Chat {chat_id} not found")

            message = Message(role=role, content=content)
            chat.messages.append(message)
            return message

    def get_chat(self, chat_id: str) -> Chat:
        chat = self.chats.get(chat_id)
        if not chat:
            raise KeyError(f"Chat {chat_id} not found")
        return chat

    # ---------- Job Methods ----------
    async def create_job(self, chat_id: str, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Job:
        async with self._lock:
            job_id = str(uuid.uuid4())
            job = Job(id=job_id, chat_id=chat_id, prompt=prompt, metadata=metadata or {})
            self.jobs[job_id] = job
            return job

    def get_job(self, job_id: str) -> Job:
        job = self.jobs.get(job_id)
        if not job:
            raise KeyError(f"Job {job_id} not found")
        return job

    async def update_job(
        self,
        job_id: str,
        status: Optional[JobStatus] = None,
        log: Optional[str] = None,
        result_message: Optional[str] = None,
        output_docx_path: Optional[str] = None,
        output_payload: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> Job:
        async with self._lock:
            job = self.jobs.get(job_id)
            if not job:
                raise KeyError(f"Job {job_id} not found")

            if status:
                job.status = status
            if log:
                job.logs.append(log)
            if result_message:
                job.result_message = result_message
            if output_docx_path:
                job.output_docx_path = output_docx_path
            if output_payload:
                job.output_payload = output_payload
            if error:
                job.error = error

            return job


# Global instance
MEMORY_STORE = MemoryStore()

