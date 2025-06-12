from dataclasses import dataclass
from typing import List
import logging

logger = logging.getLogger(__name__)


# bit 15 (QR):        0   → query
# bits 14–11 (OpCode):0000 → standard query
# bit 10 (AA):        0
# bit 9 (TC):         0
# bit 8 (RD):         1   → recursion desired
# bit 7 (RA):         0
# bits 6–4 (Z):       000
# bits 3–0 (RCODE):   0000
@dataclass
class Flags:
    qr: int
    opcode: int
    aa: int
    tc: int
    rd: int
    ra: int
    zero: int
    rcode: int

    def __str__(self) -> str:
        return (
            f"Flags:\n"
            f"  QR: {self.qr}\n"
            f"  OpCode: {self.opcode}\n"
            f"  AA: {self.aa}\n"
            f"  TC: {self.tc}\n"
            f"  RD: {self.rd}\n"
            f"  RA: {self.ra}\n"
            f"  Zero: {self.zero}\n"
            f"  Rcode: {self.rcode}"
        )


@dataclass
class Header:
    id: int
    flags: Flags
    question_count: int
    answer_rr_count: int
    authority_rr_count: int
    additional_rr_count: int

    def __str__(self) -> str:
        flags_str = str(self.flags)
        flags_indented = "\n".join("    " + line for line in flags_str.splitlines()[1:])

        return (
            f"Header:\n"
            f"  Transaction ID: {self.id:#06x}\n"
            f"  Flags:\n{flags_indented}\n"
            f"  Questions: {self.question_count}\n"
            f"  Answer RRs: {self.answer_rr_count}\n"
            f"  Authority RRs: {self.authority_rr_count}\n"
            f"  Additional RRs: {self.additional_rr_count}"
        )


@dataclass
class DNSMessage:
    header: Header
    question: List[int]
    response: List[int]
    authority: List[int]
    additional: List[int]


def parse_dns_query(data: bytes) -> Header:
    if len(data) > 512:
        raise ValueError("DNS message exceeds maximum length of 512 bytes")

    raw_header = data[:12]
    flags_int = int.from_bytes(raw_header[2:4], byteorder="big")
    logger.info(f"Raw DNS header: {raw_header.hex()}")
    header = Header(
        id=int.from_bytes(raw_header[:2]),
        flags=Flags(
            qr=(flags_int >> 15) & 0x1,
            opcode=(flags_int >> 11) & 0xF,
            aa=(flags_int >> 10) & 0x1,
            tc=(flags_int >> 9) & 0x1,
            rd=(flags_int >> 8) & 0x1,
            ra=(flags_int >> 7) & 0x1,
            zero=(flags_int >> 4) & 0x7,
            rcode=flags_int & 0xF,
        ),
        question_count=int.from_bytes(raw_header[4:6]),
        answer_rr_count=int.from_bytes(raw_header[6:8]),
        authority_rr_count=int.from_bytes(raw_header[8:10]),
        additional_rr_count=int.from_bytes(raw_header[10:12]),
    )

    logger.info(f"Parsed DNS header: {header}")

    return header
