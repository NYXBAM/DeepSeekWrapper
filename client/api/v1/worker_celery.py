
from celery import Celery
# DEFAULT CONFIG
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
    include=['client.api.v1.tasks']
)

# IF U USE DOCKER, USE redis://redis:6379/0 and redis://redis:6379/1

# celery_app = Celery(
#     "tasks",
#     broker="redis://redis:6379/0",
#     backend="redis://redis:6379/1",
#     include=['client.api.v1.tasks']
# )


celery_app.conf.result_expires = 3600

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    worker_concurrency=4 
)