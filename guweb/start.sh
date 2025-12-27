#!/bin/bash

# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.5
done
echo "Database is ready!"

# Start the application
echo "Starting guweb..."
cd /srv/root
exec poetry run hypercorn main:app --bind 0.0.0.0:8000
