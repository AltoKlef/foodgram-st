#!/bin/sh

echo "Applying migrations..."
python manage.py migrate

echo "Importing ingredients..."
python manage.py import_ingredients

echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
