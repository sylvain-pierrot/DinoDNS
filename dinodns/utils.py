def format_bits(n: int, width: int) -> str:
    return "0b" + bin(n)[2:].zfill(width)


def to_python_key(key: str) -> str:
    return key.replace("-", "_").replace("class", "class_")


def convert_keys(obj):
    if isinstance(obj, dict):
        return {to_python_key(k): convert_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys(i) for i in obj]
    else:
        return obj
