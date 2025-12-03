from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse

from ..schemas import JobCreateRequest, JobResponse
from ..services import job_service
from ..utils.logger import logger

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/{chat_id}", response_model=JobResponse)
async def create_job_for_chat(
    chat_id: str,
    req: JobCreateRequest,
    background_tasks: BackgroundTasks,
    request: Request,
):
    try:
        job = job_service.create_job(chat_id, req.prompt)
    except KeyError:
        raise HTTPException(status_code=404, detail="Chat not found")

    job_service.run_job_background(job.id, background_tasks)

    return JobResponse(
        job_id=job.id,
        status=job.status,
        chat_id=job.chat_id,
        result_message=None,
        output_docx_url=None,
        error=None,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, request: Request):
    try:
        job = job_service.get_job(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")

    base_url = str(request.base_url).rstrip("/")
    output_docx_url = None
    if job.output_docx_path:
        # served via /generated static mount
        fname = Path(job.output_docx_path).name
        output_docx_url = f"{base_url}/generated/{fname}"

    return JobResponse(
        job_id=job.id,
        status=job.status,
        chat_id=job.chat_id,
        result_message=job.result_message,
        output_docx_url=output_docx_url,
        error=job.error,
    )


@router.get("/{job_id}/download")
async def download_job_docx(job_id: str):
    try:
        job = job_service.get_job(job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Job not found")

    if not job.output_docx_path:
        raise HTTPException(status_code=404, detail="No DOCX generated for this job")

    path = Path(job.output_docx_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="DOCX file not found")

    return FileResponse(path, filename=path.name, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
