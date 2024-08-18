#!/bin/sh

# Wait for PostgreSQL to be available
until nc -z -v -w30 $POSTGRES_HOST 5432
do
  echo "Waiting for PostgreSQL database connection..."
  sleep 1
done

# Run Django management commands
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
exec "$@"
