from pathlib import Path
from typing import Optional
from fastapi import BackgroundTasks

from ..storage.memory_store import JOB_STORE, Job
from ..utils.ids import new_id
from ..services.chat_service import get_chat, add_message
from ..services.agent_registry import get_agent
from ..llm.provider_registry import create_llm_client
from ..utils.logger import logger


def create_job(chat_id: str, prompt: str) -> Job:
    job_id = new_id("job")
    job = Job(id=job_id, chat_id=chat_id, prompt=prompt)
    JOB_STORE[job_id] = job
    return job


async def _run_job_internal(job_id: str) -> None:
    job = JOB_STORE[job_id]
    job.status = "running"
    try:
        chat = get_chat(job.chat_id)
        agent = get_agent(chat.agent_id)

        llm_client = create_llm_client(chat.provider, chat.model)

        # In this demo, prompt is ABAP code input
        add_message(chat, "user", job.prompt)

        agent_result = await agent.run(
            job_id=job.id,
            prompt=job.prompt,
            llm_client=llm_client,
            chat=chat,
        )

        add_message(chat, "assistant", agent_result.text)

        job.status = "completed"
        job.result_message = agent_result.text
        job.output_docx_path = agent_result.output_docx_path
    except Exception as ex:
        logger.exception("Job %s failed", job_id)
        job.status = "failed"
        job.error = str(ex)


def run_job_background(job_id: str, background_tasks: BackgroundTasks) -> None:
    # Wrap the async executor
    async def _runner():
        await _run_job_internal(job_id)

    background_tasks.add_task(_runner)


def get_job(job_id: str) -> Job:
    job = JOB_STORE.get(job_id)
    if not job:
        raise KeyError(f"Job {job_id} not found")
    return job
