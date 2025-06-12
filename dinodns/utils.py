def format_bits(n: int, width: int) -> str:
    return "0b" + bin(n)[2:].zfill(width)
