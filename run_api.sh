#!/bin/bash

trap "kill 0" EXIT
echo "Starting DeepSeekWrapper..."
poetry run celery -A celery_worker:celery_app worker --loglevel=info --concurrency=4 &
poetry run uvicorn app:app --reload &
wait