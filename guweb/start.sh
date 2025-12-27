#!/bin/bash

# Wait for database to be ready
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done

# Start the application
cd /srv/root

# Suppress poetry output and start the app
export POETRY_VIRTUALENVS_CREATE=false
exec poetry run hypercorn main:app --bind 0.0.0.0:8000 --log-level warning --access-log - 2>&1
