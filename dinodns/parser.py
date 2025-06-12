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
    z: int
    rcode: int

    def __str__(self) -> str:
        return tabulate(
            [
                ["QR", self.qr, "Query/Response"],
                ["OpCode", hex(self.opcode), "Operation Code"],
                ["AA", hex(self.aa), "Authoritative Answer"],
                ["TC", hex(self.tc), "Truncated"],
                ["RD", hex(self.rd), "Recursion Desired"],
                ["RA", hex(self.ra), "Recursion Available"],
                ["Z", hex(self.z), "Reserved"],
                ["Rcode", hex(self.rcode), "Response Code"],
            ],
            headers=["Field", "Value", "Description"],
            colalign=("left", "left", "left"),
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
            | (self.z & 0x7) << 4
            | (self.rcode & 0xF)
        )


@dataclass
class DNSHeader:
    id: int
    flags: Flags
    qdcount: int
    ancount: int
    nscount: int
    arcount: int

    def __str__(self) -> str:
        return tabulate(
            [
                ["ID", "", hex(self.id), "Transaction ID"],
                ["Flags", "", hex(self.flags.flags_to_int()), ""],
                ["", "QR", hex(self.flags.qr), "Query/Response"],
                ["", "OpCode", hex(self.flags.opcode), "Operation Code"],
                ["", "AA", hex(self.flags.aa), "Authoritative Answer"],
                ["", "TC", hex(self.flags.tc), "Truncated"],
                ["", "RD", hex(self.flags.rd), "Recursion Desired"],
                ["", "RA", hex(self.flags.ra), "Recursion Available"],
                ["", "Z", hex(self.flags.z), "Reserved"],
                ["", "Rcode", hex(self.flags.rcode), "Response Code"],
                ["QDCOUNT", "", hex(self.qdcount), "Number of Questions"],
                ["ANCOUNT", "", hex(self.ancount), "Number of Answer RRs"],
                ["NSCOUNT", "", hex(self.nscount), "Number of Authority RRs"],
                ["ARCOUNT", "", hex(self.arcount), "Number of Additional RRs"],
            ],
            headers=["Field", "Sub-field", "Value", "Description"],
            colalign=("left", "left", "left", "left"),
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
            z=(flags_int >> 4) & 0x7,
            rcode=flags_int & 0xF,
        ),
        qdcount=int.from_bytes(raw_header[4:6]),
        ancount=int.from_bytes(raw_header[6:8]),
        nscount=int.from_bytes(raw_header[8:10]),
        arcount=int.from_bytes(raw_header[10:12]),
    )

    logger.info(f"Total data: {hex(int.from_bytes(data))}")
    for i in range(header.qdcount):
        raw_question = data[12:18]
        question = hex(int.from_bytes(data[12:18]))
        logger.info(f"Parsed question {i + 1}: {question}")

    return header
