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
    initial_offset = offset
    jumped = False
    visited_offsets = set()

    while True:
        if offset >= len(data):
            raise ValueError("decode_domain_name: offset beyond data length")

        length = data[offset]

        # Compression: pointer (starts with 11)
        if (length & 0xC0) == 0xC0:
            if offset + 1 >= len(data):
                raise ValueError("decode_domain_name: pointer truncated")

            pointer = ((length & 0x3F) << 8) | data[offset + 1]

            if pointer in visited_offsets:
                raise ValueError("decode_domain_name: compression loop")

            visited_offsets.add(pointer)

            if not jumped:
                initial_offset = offset + 2
                jumped = True

            offset = pointer
            continue

        # End of domain name
        if length == 0:
            offset += 1
            break

        offset += 1
        if offset + length > len(data):
            raise ValueError("decode_domain_name: label length out of bounds")

        label = data[offset : offset + length].decode("ascii")
        labels.append(label)
        offset += length

    domain_name = ".".join(labels) + "."
    return domain_name, (initial_offset if jumped else offset)


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
