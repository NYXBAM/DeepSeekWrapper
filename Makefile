run:
	@echo "Starting Worker and API..."
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && poetry run celery -A celery_worker:celery_app worker --loglevel=info --concurrency=4"'
	@osascript -e 'tell application "Terminal" to do script "cd $(PWD) && poetry run uvicorn app:app --reload"'