from pathlib import Path

import matplotlib.pyplot as plt
import pytest


def get_transaction_rate_from_item(item: pytest.Item) -> float | None:
    return next(
        (
            property_value
            for property_name, property_value in item.user_properties
            if property_name == 'transaction_rate'
        )
        , None
    )


def plot_and_save_data(data_x: list, data_y: list, output_image_path, graph_title):
    plt.figure(figsize=(10, 6))
    plt.plot(data_x, data_y, marker="o")
    plt.title(graph_title)
    plt.xlabel("Number of middlewares")
    plt.ylabel("Transaction rate (r/s)")
    plt.grid(True)

    # Save the plot to a file
    plt.savefig(output_image_path)
    plt.close()


def pytest_sessionfinish(session, exitstatus):
    plot_and_save_data(
        data_x=[
            item.callspec.params['num_middleware']
            for item in session.items
        ],
        data_y=[
            get_transaction_rate_from_item(item)
            for item in session.items
        ],
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
