"""
Celery application setup for ChatPwC backend.

Celery is used for executing long-running agent jobs (TS/FS generation etc.)
in the background. Broker/result backend default to Redis.
"""

import os
from celery import Celery


def make_celery() -> Celery:
    broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend = os.environ.get("CELERY_RESULT_BACKEND", broker_url)

    celery = Celery(
        "chatpwc_backend",
        broker=broker_url,
        backend=result_backend,
        include=["app.tasks"],  # our Celery tasks live here
    )

    # Optional basic config; extend as needed
    celery.conf.update(
        task_ignore_result=False,
        task_track_started=True,
        result_expires=3600,
    )

    return celery


celery_app = make_celery()
