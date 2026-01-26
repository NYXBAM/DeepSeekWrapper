from client.api.v1.worker_celery import celery_app

if __name__ == '__main__':
    celery_app.start()