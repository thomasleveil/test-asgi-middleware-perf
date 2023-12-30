import re

from matplotlib import pyplot as plt


def extract_transaction_rate(raw_text):
    """
    Extracts the transaction rate from the provided raw text.

    Args:
    raw_text (str): A string containing the raw text from which the transaction rate needs to be extracted.

    Returns:
    float: The extracted transaction rate, or None if it's not found.
    """
    # Regular expression to find the transaction rate in the text
    transaction_rate_pattern = r'Requests/sec:\s*([0-9.]+)'

    # Search for the transaction rate in the text
    match = re.search(transaction_rate_pattern, raw_text)

    # If a match is found, return the transaction rate as a float, otherwise return None
    if match:
        return float(match.group(1))
    else:
        return None


def plot_and_save_data(series: dict[str, tuple[list, list]], output_image_path, graph_title):
    plt.figure(figsize=(10, 6))
    for serie_label, (serie_x, serie_y) in series.items():
        plt.plot(serie_x, serie_y, marker="o", label=serie_label)
    plt.title(graph_title)
    plt.xlabel("Number of middlewares")
    plt.ylabel("Transaction rate (r/s)")
    plt.grid(True)

    # Place the legend below the graph
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), fancybox=True, shadow=True, ncol=1)

    # Save the plot to a file
    plt.savefig(output_image_path, bbox_inches="tight")
    plt.close()
