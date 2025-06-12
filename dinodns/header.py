from dataclasses import dataclass
from tabulate import tabulate
from utils import format_bits
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
                ["QR", bin(self.qr), "Query/Response"],
                ["OpCode", format_bits(self.opcode, 4), "Operation Code"],
                ["AA", bin(self.aa), "Authoritative Answer"],
                ["TC", bin(self.tc), "Truncated"],
                ["RD", bin(self.rd), "Recursion Desired"],
                ["RA", bin(self.ra), "Recursion Available"],
                ["Z", format_bits(self.z, 3), "Reserved"],
                ["Rcode", format_bits(self.rcode, 4), "Response Code"],
            ],
            headers=["Field", "Value", "Description"],
            colalign=("left", "left", "left"),
            tablefmt="pretty",
        )

    def to_int(self) -> int:
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

    def __init__(self, raw: bytes):
        if len(raw) != 12:
            raise ValueError("Expected exactly 12 bytes")

        flags = int.from_bytes(raw[2:4], "big")
        self.id = int.from_bytes(raw[0:2])
        self.flags = Flags(
            qr=(flags >> 15) & 0x1,
            opcode=(flags >> 11) & 0xF,
            aa=(flags >> 10) & 0x1,
            tc=(flags >> 9) & 0x1,
            rd=(flags >> 8) & 0x1,
            ra=(flags >> 7) & 0x1,
            z=(flags >> 4) & 0x7,
            rcode=flags & 0xF,
        )
        self.qdcount = int.from_bytes(raw[4:6])
        self.ancount = int.from_bytes(raw[6:8])
        self.nscount = int.from_bytes(raw[8:10])
        self.arcount = int.from_bytes(raw[10:12])

    def __str__(self) -> str:
        return tabulate(
            [
                ["ID", "", self.id.to_bytes(2, "big"), "Transaction ID"],
                ["Flags", "", self.flags.to_int().to_bytes(2, "big"), ""],
                ["", "QR", bin(self.flags.qr), "Query/Response"],
                ["", "OpCode", format_bits(self.flags.opcode, 4), "Operation Code"],
                ["", "AA", bin(self.flags.aa), "Authoritative Answer"],
                ["", "TC", bin(self.flags.tc), "Truncated"],
                ["", "RD", bin(self.flags.rd), "Recursion Desired"],
                ["", "RA", bin(self.flags.ra), "Recursion Available"],
                ["", "Z", format_bits(self.flags.z, 3), "Reserved"],
                ["", "Rcode", format_bits(self.flags.rcode, 4), "Response Code"],
                ["QDCOUNT", "", self.qdcount, "Number of Questions"],
                ["ANCOUNT", "", self.ancount, "Number of Answer RRs"],
                ["NSCOUNT", "", self.nscount, "Number of Authority RRs"],
                ["ARCOUNT", "", self.arcount, "Number of Additional RRs"],
            ],
            headers=["Field", "Sub-field", "Value", "Description"],
            colalign=("left", "left", "left", "left"),
            tablefmt="pretty",
        )
