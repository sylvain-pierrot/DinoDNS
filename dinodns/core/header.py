from dataclasses import dataclass
from enum import Enum
from typing import ClassVar
from tabulate import tabulate
from dinodns.utils import format_bits
import logging


logger = logging.getLogger(__name__)


class OpCode(Enum):
    QUERY = 0
    IQUERY = 1
    STATUS = 2


class RCode(Enum):
    NOERROR = 0
    FORMERR = 1
    SERVFAIL = 2
    NXDOMAIN = 3
    NOTIMP = 4
    REFUSED = 5
    YXDOMAIN = 6
    XRRSET = 7
    NOTAUTH = 8
    NOTZONE = 9


@dataclass
class Flags:
    qr: int
    opcode: OpCode
    aa: int
    tc: int
    rd: int
    ra: int
    z: int
    rcode: RCode

    def __str__(self) -> str:
        return (
            f"qr={self.qr} "
            f"opcode={self.opcode.name} "
            f"aa={self.aa} "
            f"tc={self.tc} "
            f"rd={self.rd} "
            f"ra={self.ra} "
            f"z={self.z} "
            f"rcode={self.rcode.name}"
        )

    def tabulate(self) -> str:
        return tabulate(
            [
                ["QR", self.qr, "Query/Response"],
                ["OpCode", format_bits(self.opcode.value, 4), "Operation Code"],
                ["AA", self.aa, "Authoritative Answer"],
                ["TC", self.tc, "Truncated"],
                ["RD", self.rd, "Recursion Desired"],
                ["RA", self.ra, "Recursion Available"],
                ["Z", format_bits(self.z, 3), "Reserved"],
                ["Rcode", format_bits(self.rcode.value, 4), "Response Code"],
            ],
            headers=["Field", "Value", "Description"],
            colalign=("left", "left", "left"),
            tablefmt="pretty",
        )

    def to_int(self) -> int:
        return (
            (self.qr & 0x1) << 15
            | (self.opcode.value & 0xF) << 11
            | (self.aa & 0x1) << 10
            | (self.tc & 0x1) << 9
            | (self.rd & 0x1) << 8
            | (self.ra & 0x1) << 7
            | (self.z & 0x7) << 4
            | (self.rcode.value & 0xF)
        )

    def to_bytes(self) -> bytes:
        return self.to_int().to_bytes(2, "big")


@dataclass
class DNSHeader:
    id: int
    flags: Flags
    qdcount: int
    ancount: int
    nscount: int
    arcount: int

    HEADER_SIZE: ClassVar[int] = 12

    def __str__(self) -> str:
        return (
            f"id={self.id} "
            f"{self.flags} "
            f"qdcount={self.qdcount} "
            f"ancount={self.ancount} "
            f"nscount={self.nscount} "
            f"arcount={self.arcount}"
        )

    def tabulate(self) -> str:
        return tabulate(
            [
                ["ID", "", self.id.to_bytes(2, "big"), "Transaction ID"],
                ["Flags", "", self.flags.to_int().to_bytes(2, "big"), ""],
                ["", "QR", self.flags.qr, "Query/Response"],
                [
                    "",
                    "OpCode",
                    format_bits(self.flags.opcode.value, 4),
                    "Operation Code",
                ],
                ["", "AA", self.flags.aa, "Authoritative Answer"],
                ["", "TC", self.flags.tc, "Truncated"],
                ["", "RD", self.flags.rd, "Recursion Desired"],
                ["", "RA", self.flags.ra, "Recursion Available"],
                ["", "Z", format_bits(self.flags.z, 3), "Reserved"],
                ["", "Rcode", format_bits(self.flags.rcode.value, 4), "Response Code"],
                ["QDCOUNT", "", self.qdcount, "Number of Questions"],
                ["ANCOUNT", "", self.ancount, "Number of Answer RRs"],
                ["NSCOUNT", "", self.nscount, "Number of Authority RRs"],
                ["ARCOUNT", "", self.arcount, "Number of Additional RRs"],
            ],
            headers=["Field", "Sub-field", "Value", "Description"],
            colalign=("left", "left", "left", "left"),
            tablefmt="pretty",
        )

    @classmethod
    def from_bytes(cls, data: bytes, offset: int) -> "DNSHeader":
        flags = int.from_bytes(data[offset + 2 : 4], "big")
        return cls(
            id=int.from_bytes(data[offset:2], "big"),
            flags=Flags(
                qr=(flags >> 15) & 0x1,
                opcode=OpCode((flags >> 11) & 0xF),
                aa=(flags >> 10) & 0x1,
                tc=(flags >> 9) & 0x1,
                rd=(flags >> 8) & 0x1,
                ra=(flags >> 7) & 0x1,
                z=(flags >> 4) & 0x7,
                rcode=RCode(flags & 0xF),
            ),
            qdcount=int.from_bytes(data[offset + 4 : 6], "big"),
            ancount=int.from_bytes(data[offset + 6 : 8], "big"),
            nscount=int.from_bytes(data[offset + 8 : 10], "big"),
            arcount=int.from_bytes(data[offset + 10 : 12], "big"),
        )

    def to_bytes(self) -> bytes:
        return (
            self.id.to_bytes(2, "big")
            + self.flags.to_bytes()
            + self.qdcount.to_bytes(2, "big")
            + self.ancount.to_bytes(2, "big")
            + self.nscount.to_bytes(2, "big")
            + self.arcount.to_bytes(2, "big")
        )

    def byte_length(self) -> int:
        return len(self.to_bytes())
