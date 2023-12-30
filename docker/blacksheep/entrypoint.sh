#!/bin/bash
echo "number of middlewares : ${NUM_MIDDLEWARES:?}"
nohup gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:14000 server:app &
sleep 1
wrk --duration=30s --threads=4 --connections=64 --timeout=5s http://127.0.0.1:14000/_ping 2>&1
sleep 5

echo -----------------------------------------
python --version
pip list
echo "number of middlewares : $NUM_MIDDLEWARES"
echo "EndOfLog"
