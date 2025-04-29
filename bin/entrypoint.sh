#!/bin/bash
set -e

echo "Running migrations..."
uv run src/manage.py migrate

echo "Starting Django app..."
uv run src/manage.py runserver 0.0.0.0:8000
