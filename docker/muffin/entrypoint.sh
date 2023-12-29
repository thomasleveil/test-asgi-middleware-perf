#!/bin/bash
echo "---$0---"
num_middleware=$1
num_queries=${2:-50000}
threads=4
repetitions=$(( num_queries / threads ))

echo -----------------------------------------
echo "number of middlewares : ${num_middleware:?}"
python --version
pip list | grep -i muffin
pip list | grep -i uvicorn
echo -----------------------------------------

nohup python server.py $num_middleware &
sleep 5
siege -r $repetitions -c $threads http://127.0.0.1:14000/_ping 2>&1
sleep 5
echo -----------------------------------------
echo "number of middlewares : $num_middleware"
python --version
pip list | grep -i muffin
pip list | grep -i uvicorn
echo "EndOfLog"
