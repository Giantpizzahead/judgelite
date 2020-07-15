#!/bin/sh

# Start the redis server
redis-server --daemonize yes

# Make sure the redis server starts first
sleep 3

# Start a worker for submissions
python3 worker.py &

# Start the web server
gunicorn -c gunicorn.conf.py app:app

# top