#!/bin/sh

echo "Applying migrations..."
python manage.py migrate

echo "Importing ingredients..."
python manage.py import_ingredients


echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn server..."
exec gunicorn foodgram.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3