from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pytest


def get_custom_property(item: pytest.Item, prop_name: str) -> Any:
    return next(
        (
            property_value
            for property_name, property_value in item.user_properties
            if property_name == prop_name
        )
        , None
    )


def get_serie_from_item(item: pytest.Item) -> float | None:
    return get_custom_property(item, "serie")


def get_transaction_rate_from_item(item: pytest.Item) -> float | None:
    return get_custom_property(item, "transaction_rate")


def plot_and_save_data(series: dict[str, tuple[list, list]], output_image_path, graph_title):
    plt.figure(figsize=(10, 6))
    for serie_label, (serie_x, serie_y) in series.items():
        plt.plot(serie_x, serie_y, marker="o", label=serie_label)
    plt.title(graph_title)
    plt.xlabel("Number of middlewares")
    plt.ylabel("Transaction rate (r/s)")
    plt.grid(True)
    plt.legend()
    # Save the plot to a file
    plt.savefig(output_image_path)
    plt.close()


def pytest_sessionfinish(session, exitstatus):
    series = defaultdict(lambda: (list(), list()))

    for item in session.items:
        serie_name = get_serie_from_item(item)
        num_middlewares = item.callspec.params['num_middleware']
        transaction_rate = get_transaction_rate_from_item(item)
        series[serie_name][0].append(num_middlewares)
        series[serie_name][1].append(transaction_rate)

    plot_and_save_data(
        series=series,
        output_image_path=Path(__file__).parent / '../test_results/summary.png',
        graph_title='Performances vs number of middlewares',
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.transaction_rate = None
    if report.when == "call":
        report.transaction_rate = get_transaction_rate_from_item(item)


def pytest_html_report_title(report):
    report.title = "Starlette performance report"


def pytest_html_results_table_header(cells):
    cells.insert(2, "<th>Transaction rate</th>")


def pytest_html_results_table_row(report, cells):
    cells.insert(2, f"<td>{report.transaction_rate}</td>")
