import logging
from celery import Celery

from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery app
# Using Redis as both the message broker and backend database for storing execution results.
celery_app = Celery(
    "finance_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.services.tasks"]  # Auto-discover tasks module
)

# Production configurations
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # Keep worker processes responsive
    worker_prefetch_multiplier=1,
)

logger.info("Celery task queue worker initialized successfully.")
