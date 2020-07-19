#!/bin/bash

echo "Installing pytest and curl..."
pip3 install pytest pytest-cov
apt-get install -y curl

echo "Setting up environment..."

# Copied from start.sh
isolate/isolate-check-environment --execute
redis-server --daemonize yes
sleep 3
python3 worker.py &
nice -n -10 gunicorn -c gunicorn.conf.py app:app &

# Make sure the web server finishes starting
sleep 3

echo "Running pytest..."
pytest -W ignore::DeprecationWarning --cov-report=xml --cov=./

echo "Uploading coverage report..."
bash <(curl -s https://codecov.io/bash) || echo "WARNING: Codecov did not collect coverage reports!"
