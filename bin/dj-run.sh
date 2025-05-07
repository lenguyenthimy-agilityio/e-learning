#!/bin/bash

PORT=$1

if [ "$PORT" = "" ]; then
    PORT='8000'
fi

uv run src/manage.py runserver 0.0.0.0:${PORT}
