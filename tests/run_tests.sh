#!/bin/bash

# Set debug environment variables
export DEBUG=1
export DEBUG_LOW=1
export DEBUG_LOWEST=1
export PROGRAM_OUTPUT=64

# Source: https://unix.stackexchange.com/a/267730
center() {
  termwidth=80
  padding="$(printf '%0.1s' ={1..500})"
  printf '%*.*s %s %*.*s\n' 0 "$(((termwidth-2-${#1})/2))" "$padding" "$1" 0 "$(((termwidth-1-${#1})/2))" "$padding"
}

center "setting up environment"
# Install pytest
echo "Installing pytest..."
pip3 install --quiet pytest pytest-cov

# Copied from start.sh
echo "Configuring isolate settings..."
misc/isolate-check-environment.sh --execute
echo "Starting redis server..."
redis-server misc/redis.conf & # </dev/null &>/dev/null &
sleep 1.5
echo "Starting rq worker..."
python3 worker.py & # </dev/null &>/dev/null &
echo "Starting gunicorn server..."
nice -n -10 gunicorn -c misc/gunicorn.conf.py app:app & # </dev/null &>/dev/null &
echo "Setup complete!"

# Make sure the web server finishes starting, then run pytest
sleep 2
echo ""
pytest -W ignore::DeprecationWarning --cov-report=xml --cov=./
PYTEST_RESULT=$?

# Move coverage info out of Docker container
mv .coverage ../shared/
mv coverage.xml ../shared/

# Return pytest's exit code (to tell Github Actions if the tests passed or not).
exit $PYTEST_RESULT
