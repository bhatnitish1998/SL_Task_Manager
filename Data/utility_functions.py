def kb_to_print(value):
    result = f"{value:.2f} KB"
    if value > 1024:
        value = value / 1024
        result = f"{value:.2f} MB"
    if value > 1024:
        value = value / 1024
        result = f"{value:.2f} GB"
    return result