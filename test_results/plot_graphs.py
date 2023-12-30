import re
from collections import defaultdict
from pathlib import Path

from utils import extract_transaction_rate, plot_and_save_data

if __name__ == '__main__':
    # plot graph from data found in logs
    test_results_dir = Path(__file__).parent

    re_versions = re.compile(
        r'^(?P<asgi_name>\w+)_\w(?P<asgi_version>[.\d]+)_p(?P<python_version>[.\d]+)_u(?P<uvicorn_version>[.\d]+)_middleware-(?P<middleware_number>\d+)_docker.log$')

    for log_dir in test_results_dir.iterdir():
        if not log_dir.is_dir():
            continue
        print(f"Processing dir: {log_dir.name}")

        series = defaultdict(lambda: (list(), list()))
        for log_file_path in sorted(log_dir.glob('*.log')):
            m = re_versions.match(log_file_path.name)
            if m is None:
                raise ValueError("couldn't parse log file name data")

            serie_name = f"{m.group('asgi_name')} {m.group('asgi_version')}, Python {m.group('python_version')}, Uvicorn {m.group('uvicorn_version')}"
            num_middlewares = int(m.group('middleware_number'))

            transaction_rate = extract_transaction_rate(log_file_path.read_text())
            series[serie_name][0].append(num_middlewares)
            series[serie_name][1].append(transaction_rate)

        plot_and_save_data(
            series=series,
            output_image_path=test_results_dir / f'{log_dir.name}.png',
            graph_title='Performances vs number of middlewares',
        )
