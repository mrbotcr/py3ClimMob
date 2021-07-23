#celery -A climmob.config.celery_app worker -Q ClimMob --loglevel=info --broker=redis://localhost:6379/5 --result-backend=redis://localhost:6379/5

#celery -A climmob.config.celery_app worker -Q ClimMob --loglevel=info --broker=redis://localhost:6379/5 --result-backend=redis://localhost:6379/5 --concurrency=3

#celery -A climmob.config.celery_app worker -Q ClimMob --loglevel=info --concurrency=3 --pool=solo

#celery -A climmob.config.celery_app worker -Q ClimMob --loglevel=info --concurrency=3 --logfile="/home/bmadriz/Desktop/a.log"

celery -A climmob.config.celery_app worker -Q ClimMob --loglevel=info --concurrency=3