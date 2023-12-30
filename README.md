# Performance test suite for ASGI frameworks

This project is a test suite trying to detect performance issues when using middlewares with 
ASGI frameworks.

The middleware is doing almost nothing. We just test the effect on performances of having middlewares.

## Results


![](report/summary.png)

---- 

## Requirements

- docker
- python 3.10+

```shell
git clone https://github.com/thomasleveil/test-starlette-middleware-perf.git
cd test-starlette-middleware-perf
pip install -r requirements.txt
```

## Usage

```shell
pytest
```


## Configuration

See the top section of [tests/test_perf.py](tests/test_perf.py)

## Hack

- A Docker image is built with the configured version of the ASGI framework, Python and Uvicorn.
  See Dockerfiles in [docker/*](docker/)
- The server implementation is minimal. See [docker/*/server.py](docker/)
- Performance tests are performed using Siege. See [docker/*/entrypoint.sh](docker/)
- Pytest is used to create and run a docker container with a parametrized number of middlewares.
  See [test_perf.py](tests/test_perf.py)

