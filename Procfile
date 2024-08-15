web: python manage.py migrate && gunicorn config.wsgi
worker: celery -A config worker --loglevel=info
