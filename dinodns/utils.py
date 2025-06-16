from typing import Any, List, Tuple


def format_bits(n: int, width: int) -> str:
    return "0b" + bin(n)[2:].zfill(width)


KEY_REPLACEMENTS = {
    "domain-name": "domain_name",
    "host-address": "host_address",
    "class": "class_",
}


def to_python_key(key: str) -> str:
    return KEY_REPLACEMENTS.get(key, key)


def convert_keys(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {to_python_key(str(k)): convert_keys(v) for k, v in obj.items()}  # type: ignore
    elif isinstance(obj, list):
        return [convert_keys(i) for i in obj]  # type: ignore
    else:
        return obj


def encode_domain_name(domain: str) -> bytes:
    parts = domain.rstrip(".").split(".")
    return (
        b"".join(len(label).to_bytes(1, "big") + label.encode() for label in parts)
        + b"\x00"
    )


def decode_domain_name(data: bytes, offset: int = 0) -> Tuple[str, int]:
    labels: List[str] = []
    jumped = False
    original_offset = offset

    while True:
        length = data[offset]

        if (length & 0xC0) == 0xC0:
            pointer = ((length & 0x3F) << 8) | data[offset + 1]
            if not jumped:
                original_offset = offset + 2
                jumped = True
            offset = pointer
            continue

        if length == 0:
            offset += 1
            break

        offset += 1
        labels.append(data[offset : offset + length].decode())
        offset += length

    domain_name = ".".join(labels) + "."
    return domain_name, (original_offset if jumped else offset)


def encode_email(email: str) -> bytes:
    if "@" not in email:
        raise ValueError("Invalid email: missing '@'")

    parts = email.rstrip(".").split("@")
    return (
        b"".join(len(label).to_bytes(1, "big") + label.encode() for label in parts)
        + b"\x00"
    )


def decode_email(data: bytes) -> Tuple[str, int]:
    labels: list[str] = []
    offset = 0
    while data[offset] != 0:
        length = data[offset]
        offset += 1
        labels.append(data[offset : offset + length].decode())
        offset += length
    offset += 1  # null terminator
    result = "@".join(labels)
    return result, offset
