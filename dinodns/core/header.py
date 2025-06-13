from dataclasses import dataclass
from tabulate import tabulate
from dinodns.utils import format_bits
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
                ["OpCode", format_bits(self.opcode, 4), "Operation Code"],
                ["AA", self.aa, "Authoritative Answer"],
                ["TC", self.tc, "Truncated"],
                ["RD", self.rd, "Recursion Desired"],
                ["RA", self.ra, "Recursion Available"],
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

    def __str__(self) -> str:
        return tabulate(
            [
                ["ID", "", self.id.to_bytes(2, "big"), "Transaction ID"],
                ["Flags", "", self.flags.to_int().to_bytes(2, "big"), ""],
                ["", "QR", self.flags.qr, "Query/Response"],
                ["", "OpCode", format_bits(self.flags.opcode, 4), "Operation Code"],
                ["", "AA", self.flags.aa, "Authoritative Answer"],
                ["", "TC", self.flags.tc, "Truncated"],
                ["", "RD", self.flags.rd, "Recursion Desired"],
                ["", "RA", self.flags.ra, "Recursion Available"],
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

    @classmethod
    def from_bytes(cls, data: bytes) -> "DNSHeader":
        if len(data) != 12:
            raise ValueError("Expected exactly 12 bytes for DNS header")

        flags = int.from_bytes(data[2:4], "big")
        return cls(
            id=int.from_bytes(data[0:2], "big"),
            flags=Flags(
                qr=(flags >> 15) & 0x1,
                opcode=(flags >> 11) & 0xF,
                aa=(flags >> 10) & 0x1,
                tc=(flags >> 9) & 0x1,
                rd=(flags >> 8) & 0x1,
                ra=(flags >> 7) & 0x1,
                z=(flags >> 4) & 0x7,
                rcode=flags & 0xF,
            ),
            qdcount=int.from_bytes(data[4:6], "big"),
            ancount=int.from_bytes(data[6:8], "big"),
            nscount=int.from_bytes(data[8:10], "big"),
            arcount=int.from_bytes(data[10:12], "big"),
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
