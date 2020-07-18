#!/bin/sh

echo "Installing pytest..."
pip3 install pytest pytest-cov

echo "Starting pytest..."
pytest -W ignore::DeprecationWarning --cov-report=xml --cov=app --cov=judge_submission
