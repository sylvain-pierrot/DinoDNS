from dataclasses import dataclass
from typing import List
from tabulate import tabulate
import logging

logger = logging.getLogger(__name__)


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
        return tabulate(
            [
                ["QR", self.qr],
                ["OpCode", hex(self.opcode)],
                ["AA", hex(self.aa)],
                ["TC", hex(self.tc)],
                ["RD", hex(self.rd)],
                ["RA", hex(self.ra)],
                ["Z", hex(self.zero)],
                ["Rcode", hex(self.rcode)],
            ],
            headers=["Field", "Value"],
            tablefmt="pretty",
        )

    def flags_to_int(self) -> int:
        return (
            (self.qr & 0x1) << 15
            | (self.opcode & 0xF) << 11
            | (self.aa & 0x1) << 10
            | (self.tc & 0x1) << 9
            | (self.rd & 0x1) << 8
            | (self.ra & 0x1) << 7
            | (self.zero & 0x7) << 4
            | (self.rcode & 0xF)
        )


@dataclass
class DNSHeader:
    id: int
    flags: Flags
    question_count: int
    answer_rr_count: int
    authority_rr_count: int
    additional_rr_count: int

    def __str__(self) -> str:
        return tabulate(
            [
                ["ID", "", hex(self.id)],
                ["Flags", "", hex(self.flags.flags_to_int())],
                ["", "QR", hex(self.flags.qr)],
                ["", "OpCode", hex(self.flags.opcode)],
                ["", "AA", hex(self.flags.aa)],
                ["", "TC", hex(self.flags.tc)],
                ["", "RD", hex(self.flags.rd)],
                ["", "RA", hex(self.flags.ra)],
                ["", "Zero", hex(self.flags.zero)],
                ["", "Rcode", hex(self.flags.rcode)],
                ["QDCOUNT", "", hex(self.question_count)],
                ["ANCOUNT", "", hex(self.answer_rr_count)],
                ["NSCOUNT", "", hex(self.authority_rr_count)],
                ["ARCOUNT", "", hex(self.additional_rr_count)],
            ],
            headers=["Field", "Sub-field", "Value"],
            tablefmt="pretty",
        )


@dataclass
class DNSQuestion:
    qname: int
    qtype: int
    qclass: int


@dataclass
class DNSMessage:
    header: DNSHeader
    question: List[DNSQuestion]
    response: List[int]
    authority: List[int]
    additional: List[int]


def parse_dns_query(data: bytes) -> DNSHeader:
    if len(data) > 512:
        raise ValueError("DNS message exceeds maximum length of 512 bytes")

    raw_header = data[:12]
    flags_int = int.from_bytes(raw_header[2:4], byteorder="big")
    header = DNSHeader(
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

    logger.info(f"Total data: {hex(int.from_bytes(data))}")
    for i in range(header.question_count):
        question = hex(int.from_bytes(data[12:18]))
        logger.info(f"Parsed question {i + 1}: {question}")

    return header
