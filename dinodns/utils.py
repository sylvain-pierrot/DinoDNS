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


def encode_domain_name(domain: str) -> bytes:
    parts = domain.rstrip(".").split(".")
    return (
        b"".join(len(label).to_bytes(1, "big") + label.encode() for label in parts)
        + b"\x00"
    )


def decode_domain_name(data: bytes) -> str:
    labels = []
    offset = 0
    while data[offset] != 0:
        length = data[offset]
        offset += 1
        labels.append(data[offset : offset + length].decode())
        offset += length
    return ".".join(labels) + "."
