"""
Celery tasks for ChatPwC backend.
Each task runs an agent against a chat/job and updates job_manager & memory_store.
"""

import asyncio
from typing import Optional

from celery import shared_task

from .services.job_manager import job_manager, JobStatus
from .services.chat_service import get_chat, add_message
from .services.agent_registry import get_agent
from .llm.provider_registry import create_llm_client
from .storage.memory_store import JOB_STORE
from .utils.logger import logger


async def _run_job(job_id: str) -> None:
    job = JOB_STORE.get(job_id)
    if not job:
        logger.error(f"[Celery] Job {job_id} not found in JOB_STORE")
        return

    chat = get_chat(job.chat_id)
    agent = get_agent(chat.agent_id)
    llm_client = create_llm_client(chat.provider, chat.model)

    await job_manager.update_job(job_id, JobStatus.RUNNING, log="Starting agent execution")

    try:
        # Take last user message or prompt string
        prompt = job.prompt

        logger.info(f"[Celery] Running agent {agent.name} for job {job_id}")
        result = await agent.run(
            chat=chat,
            llm_client=llm_client,
            job_id=job_id,
            prompt=prompt,
        )

        # Update chat history
        add_message(chat, "assistant", result.text)

        # Update Job dataclass
        job.status = "completed"
        job.result_message = result.text
        job.output_docx_path = result.output_docx_path

        await job_manager.update_job(
            job_id,
            JobStatus.COMPLETED,
            log="Job completed successfully",
            result={
                "result_message": result.text,
                "output_docx_path": result.output_docx_path,
            },
        )

    except Exception as exc:
        logger.exception(f"[Celery] Job {job_id} failed: {exc}")
        job.status = "failed"
        job.error = str(exc)
        await job_manager.update_job(
            job_id,
            JobStatus.FAILED,
            log=f"Job failed: {exc}",
            result=None,
        )
        raise


@shared_task(name="run_agent_job")
def run_agent_job(job_id: str) -> None:
    """
    Celery entry point. Runs the async _run_job inside an event loop.
    """
    asyncio.run(_run_job(job_id))
