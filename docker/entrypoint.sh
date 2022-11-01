#!/bin/sh
export GIT_COMMIT=$(git rev-parse --short HEAD)
poetry run uvicorn "app.main:app" --host 0.0.0.0 --port $PORT