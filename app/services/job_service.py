from typing import Optional
from ..storage.memory_store import MEMORY_STORE, Job
from ..utils.ids import new_id
from ..services.chat_service import get_chat
from ..services.job_manager import job_manager
from ..utils.logger import logger

# Lazy import so FastAPI can start without Celery
def enqueue_job(job_id: str) -> None:
    from ..tasks import run_agent_job
    logger.info(f"[JobService] Enqueuing job {job_id} to Celery")
    run_agent_job.apply_async(args=[job_id])


async def create_job(chat_id: str, prompt: str) -> Job:
    chat = get_chat(chat_id)

    job_id = new_id("job")
    job = Job(id=job_id, chat_id=chat_id, prompt=prompt)
    MEMORY_STORE.jobs[job_id] = job   # FIXED storage usage

    await job_manager.create_job(metadata={"chat_id": chat_id, "agent_id": chat.agent_id})

    logger.info(f"[JobService] Created job {job_id} for chat {chat_id}")
    return job


def get_job(job_id: str) -> Job:
    job = MEMORY_STORE.jobs.get(job_id)
    if not job:
        raise KeyError(f"Job {job_id} not found")
    return job
