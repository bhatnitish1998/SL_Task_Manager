def kb_to_print(value):
    result = f"{value:.2f} KB"
    if value > 1024:
        value = value / 1024
        result = f"{value:.2f} MB"
    if value > 1024:
        value = value / 1024
        result = f"{value:.2f} GB"
    return result


def b_to_print(value):
    result = f"{value:.2f} B"
    if value > 1024:
        return kb_to_print(round(value/1024))
    return result


def bytes_to_kilobytes(bytes_val: float) -> float:
    """
    Converts a number of bytes per second to kilobytes per second.
    """
    return bytes_val / 1024


def bytes_to_megabytes(bytes_val: float) -> float:
    """
    Converts a number of bytes per second to megabytes per second.
    """
    return bytes_val / (1024 * 1024)


def bytes_to_gigabytes(bytes_val: float) -> float:
    """
    Converts a number of bytes per second to gigabytes per second.
    """
    return bytes_val / (1024 * 1024 * 1024)
