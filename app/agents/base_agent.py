from dataclasses import dataclass
from typing import Optional
from ..llm.base import LLMClient
from ..storage.memory_store import ChatSession


@dataclass
class AgentResult:
    text: str
    output_docx_path: Optional[str] = None


class BaseAgent:
    id: str
    name: str
    description: str

    async def run(
        self,
        job_id: str,
        prompt: str,
        llm_client: LLMClient,
        chat: ChatSession,
    ) -> AgentResult:
        raise NotImplementedError
