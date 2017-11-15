#!/bin/bash

# Apply updates for binarization microservice
./manage.py makemigrations
./manage.py migrate

# Start Gunicorn processes
echo Starting Gunicorn.
# Running server to port 8003. Specify the # threads that will handle the requests coming to binarization service
exec gunicorn RecognitionService.wsgi:application --bind 0.0.0.0:8003 --workers 3
