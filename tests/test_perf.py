"""
Test module performing the benchmark
"""
import json

from utils.bombardier import run_bombardier


def test_perf(record_property, results_dir, asgi_server):
    server_env, num_middlewares, container, test_log_dir = asgi_server

    logs = run_bombardier(f"http://{container.network_settings.ip_address}/_ping")
    bombardier_data = json.loads(logs.splitlines()[-1])
    transaction_rate = bombardier_data["result"]["rps"]["percentiles"]["99"]
    print(f"Transaction rate : {transaction_rate} r/s")

    with (test_log_dir / f"bombardier.log").open(mode="w") as f:
        pretty_logs = json.dumps(bombardier_data, indent=4)
        print(pretty_logs)
        f.write(pretty_logs + "\n")
        f.write(f"Transaction rate : {transaction_rate} r/s")

    assert transaction_rate is not None
    record_property("transaction_rate", transaction_rate)
    record_property("num_middlewares", num_middlewares)
    record_property(
        "serie",
        f"{server_env.asgi_module} {server_env.asgi_version}, "
        f"Python {server_env.python}, "
        f"Gunicorn {server_env.gunicorn}, "
        f"Uvicorn {server_env.uvicorn}"
    )
    record_property("results_dir", results_dir)
