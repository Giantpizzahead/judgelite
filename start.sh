#!/bin/sh

# Configure environment for the isolate sandbox
isolate/isolate-check-environment --execute

# Start the redis server
redis-server --daemonize yes

# Make sure the redis server starts first
sleep 3

# Start a worker for submissions
python3 worker.py &

# Start the web server with high priority
nice -n -10 gunicorn -c gunicorn.conf.py app:app

# top