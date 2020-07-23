#!/bin/sh

# Don't test anything if on Docker Hub
if [ ! -d "/shared" ]
then
  echo "Skipping tests (on Docker Hub)."
  exit 0
fi

# Set debug environment variables
export DEBUG=1
export DEBUG_LOW=1
export DEBUG_LOWEST=1
export PROGRAM_OUTPUT=64

echo "=============================setting up environment============================="
# Install pytest
echo "Installing pytest..."
pip3 install --quiet pytest pytest-cov

# Copied from start.sh
echo "Configuring isolate settings..."
misc/isolate-check-environment --execute
echo "Starting redis server..."
mkdir -p /redis_db
redis-server misc/redis.conf </dev/null >/dev/null 2>&1 &
sleep 1.5
echo "Starting rq worker..."
python3 worker.py </dev/null >/dev/null 2>&1 &
echo "Starting gunicorn server..."
nice -n -10 gunicorn -c misc/gunicorn.conf.py app:app </dev/null >/dev/null 2>&1 &
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
