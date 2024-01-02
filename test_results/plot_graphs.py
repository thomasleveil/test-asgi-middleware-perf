import re
from collections import defaultdict
from pathlib import Path

from utils import plot_and_save_data, extract_transaction_rate

re_versions = re.compile(
    r'^(?P<asgi_name>\w+)_(?P<asgi_version>[^_]+)__p(?P<python_version>[^_]+)_g(?P<gunicorn_version>[^_]+)_u(?P<uvicorn_version>[^_]+)_middleware-(?P<middleware_number>\d+)$')


def plot_bombardier_results(log_dir: Path):
    series = defaultdict(lambda: (list(), list()))
    for log_file_path in sorted(log_dir.glob('*/bombardier.log')):
        m = re_versions.match(log_file_path.parent.name)
        if m is None:
            raise ValueError(f"couldn't parse log file name data {log_file_path.parent.name}")

        serie_name = f"{m.group('asgi_name')} {m.group('asgi_version')}, Python {m.group('python_version')}, Gunicorn {m.group('gunicorn_version')}, Uvicorn {m.group('uvicorn_version')}"
        num_middlewares = int(m.group('middleware_number'))

        bombardier_log = log_file_path.read_text()

        transaction_rate = extract_transaction_rate(bombardier_log)
        series[serie_name][0].append(num_middlewares)
        series[serie_name][1].append(transaction_rate)

    plot_and_save_data(
        series=series,
        output_image_path=log_dir / f'results_bombardier.png',
        graph_title='Performances vs number of middlewares',
    )


if __name__ == '__main__':
    # plot graph from data found in logs
    test_results_dir = Path(__file__).parent

    for log_dir in test_results_dir.iterdir():
        if not log_dir.is_dir():
            continue
        print(f"Processing dir: {log_dir.name}")
        plot_bombardier_results(log_dir)
