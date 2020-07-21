#!/bin/bash

# Configure environment for the isolate sandbox
misc/isolate-check-environment --execute

# Start the redis server
mkdir -p /redis_db
redis-server misc/redis.conf &

# Make sure the redis server starts first
sleep 1.5

# Start a worker for submissions
python3 worker.py &

# Start the web server with high priority
nice -n -10 gunicorn -c misc/gunicorn.conf.py app:app

# top