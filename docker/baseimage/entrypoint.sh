#!/bin/bash
echo "number of middlewares : ${NUM_MIDDLEWARES:?}"
python --version
pip list
echo -----------------------------------------
gunicorn --workers=1 --worker-class uvicorn.workers.UvicornWorker -b 0.0.0.0:80 server:app
