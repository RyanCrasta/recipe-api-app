#!/bin/sh

set -e  # Exit immediately if a command exits with a non-zero status

# Run Django database migrations
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Collect static files (optional, if you're serving static files)
python manage.py collectstatic --no-input

# Start the Django server
python manage.py runserver 0.0.0.0:8000
