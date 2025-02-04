def parse_value(value):
    """
    Parses a string value in hex, binary, or decimal format.

    Args:
        value (str): The value to parse.

    Returns:
        int: The parsed integer value.

    Raises:
        ValueError: If the format is invalid.
    """
    value_lower = value.lower()
    if value_lower.startswith("0x"):
        return int(value, 16)
    elif value_lower.startswith("0b"):
        return int(value, 2)
    else:
        return int(value)