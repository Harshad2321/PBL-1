#!/bin/bash
cd "$(dirname "$0")"
python3 -m uvicorn api_server:app --host 127.0.0.1 --port 8000 &
sleep 3
echo "Backend started on port 8000"
