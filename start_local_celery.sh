celery -A climmob.config.celery_app worker --loglevel=info --broker=redis://localhost:6379/5 --result-backend=redis://localhost:6379/5
