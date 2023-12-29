import re


def extract_transaction_rate(raw_text):
    """
    Extracts the transaction rate from the provided raw text.

    Args:
    raw_text (str): A string containing the raw text from which the transaction rate needs to be extracted.

    Returns:
    float: The extracted transaction rate, or None if it's not found.
    """
    # Regular expression to find the transaction rate in the text
    transaction_rate_pattern = r'"transaction_rate":\s*([0-9.]+)'

    # Search for the transaction rate in the text
    match = re.search(transaction_rate_pattern, raw_text)

    # If a match is found, return the transaction rate as a float, otherwise return None
    if match:
        return float(match.group(1))
    else:
        return None
