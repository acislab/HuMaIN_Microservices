#!/bin/bash

# Apply updates for binarization microservice
./manage.py makemigrations
./manage.py migrate

# Start Gunicorn processes
echo Starting Gunicorn.
# Running server to port 8001. Specify the # threads that will handle the requests coming to binarization service
exec gunicorn BinarizationService.wsgi:application --bind 0.0.0.0:8001 --workers 3
