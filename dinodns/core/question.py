from dataclasses import dataclass
from enum import Enum
import logging
from typing import List


logger = logging.getLogger(__name__)


class QType(Enum):
    UNKNOWN = -1
    A = 1
    NS = 2
    MD = 3
    MF = 4
    CNAME = 5
    SOA = 6
    MB = 7
    MG = 8
    MR = 9
    NULL = 10
    WKS = 11
    PTR = 12
    HINFO = 13
    MINFO = 14
    MX = 15
    TXT = 16
    AAAA = 28
    SRV = 33
    AXFR = 252
    MAILB = 253
    MAILA = 254
    ANY = 255

    @classmethod
    def _missing_(cls, value: object):
        obj = object.__new__(cls)
        obj._name_ = "UNKNOWN"
        obj._value_ = value
        return obj


class QClass(Enum):
    UNKNOWN = -1
    IN = 1  # Internet class
    CS = 2  # CSNET class (obsolete)
    CH = 3  # CHAOS class (obsolete)
    HS = 4  # Hesiod class (obsolete)
    ANY = 255

    @classmethod
    def _missing_(cls, value: object):
        obj = object.__new__(cls)
        obj._name_ = "UNKNOWN"
        obj._value_ = value
        return obj


@dataclass
class DNSQuestion:
    qname: str
    qtype: QType
    qclass: QClass

    def __str__(self) -> str:
        return f"qname={self.qname} qtype={self.qtype.name} qclass={self.qclass.name}"

    def to_logfmt(self, index: int) -> str:
        return (
            f"question.{index}.qname={self.qname} "
            f"question.{index}.qtype={self.qtype.name} "
            f"question.{index}.qclass={self.qclass.name}"
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "DNSQuestion":
        offset = 0
        labels: List[str] = []
        while data[offset] != 0:
            length = data[offset]
            offset += 1
            labels.append(data[offset : offset + length].decode())
            offset += length
        offset += 1  # skip null byte
        qname = ".".join(labels) + "."
        qtype = QType(int.from_bytes(data[offset : offset + 2], "big"))
        qclass = QClass(int.from_bytes(data[offset + 2 : offset + 4], "big"))
        return cls(qname=qname, qtype=qtype, qclass=qclass)

    def to_bytes(self) -> bytes:
        qname_bytes = (
            b"".join(
                len(label).to_bytes(1, "big") + label.encode()
                for label in self.qname.rstrip(".").split(".")
            )
            + b"\x00"
        )
        qtype_bytes = self.qtype.value.to_bytes(2, "big")
        qclass_bytes = self.qclass.value.to_bytes(2, "big")
        return qname_bytes + qtype_bytes + qclass_bytes

    def byte_length(self) -> int:
        return len(self.to_bytes())
    