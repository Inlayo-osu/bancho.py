#!/bin/bash

# Wait for database to be ready
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done

# Start the application
cd /srv/root

# Suppress poetry warnings
export POETRY_VIRTUALENVS_CREATE=false
export POETRY_NO_INTERACTION=1

# Run hypercorn with error level only (no startup logs from hypercorn)
exec poetry run hypercorn main:app --bind 0.0.0.0:8000 --log-level error --access-log -
