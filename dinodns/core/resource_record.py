from abc import ABC, abstractmethod
from enum import Enum
from ipaddress import IPv4Address
from dataclasses import dataclass
from typing import List
from dinodns.utils import decode_domain_name, encode_domain_name
import logging

logger = logging.getLogger(__name__)


class Type(Enum):
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

    @classmethod
    def _missing_(cls, value: object):
        obj = object.__new__(cls)
        obj._name_ = "UNKNOWN"
        obj._value_ = value
        return obj


class Class(Enum):
    UNKNOWN = -1
    IN = 1  # Internet class
    CS = 2  # CSNET class (obsolete)
    CH = 3  # CHAOS class (obsolete)
    HS = 4  # Hesiod class (obsolete)

    @classmethod
    def _missing_(cls, value: object):
        obj = object.__new__(cls)
        obj._name_ = "UNKNOWN"
        obj._value_ = value
        return obj


class RData(ABC):
    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes) -> "RData":
        raise NotImplementedError()

    @abstractmethod
    def to_bytes(self) -> bytes:
        raise NotImplementedError()


@dataclass
class RDataA(RData):
    address: IPv4Address

    @classmethod
    def from_bytes(cls, data: bytes) -> "RDataA":
        return cls(address=IPv4Address(data))

    def to_bytes(self) -> bytes:
        return self.address.packed


@dataclass
class RDataCNAME(RData):
    cname: str

    @classmethod
    def from_bytes(cls, data: bytes) -> "RDataCNAME":
        return cls(cname=decode_domain_name(data))

    def to_bytes(self) -> bytes:
        return encode_domain_name(self.cname)


@dataclass
class RDataNS(RData):
    nsdname: str

    @classmethod
    def from_bytes(cls, data: bytes) -> "RDataNS":
        return cls(nsdname=decode_domain_name(data))

    def to_bytes(self) -> bytes:
        return encode_domain_name(self.nsdname)


class RDataFactory:
    _registry: dict[Type, type[RData]] = {
        Type.A: RDataA,
        Type.CNAME: RDataCNAME,
        Type.NS: RDataNS,
    }

    @staticmethod
    def from_bytes(qtype: Type, data: bytes) -> RData:
        cls = RDataFactory._registry.get(qtype)
        if cls is None:
            raise NotImplementedError(f"Unsupported QType: {qtype}")
        return cls.from_bytes(data)


@dataclass
class DNSResourceRecord:
    name: str
    type: Type
    class_: Class
    ttl: int
    rdata: RData

    def __str__(self) -> str:
        if isinstance(self.rdata, RDataA):
            rdata_str = str(self.rdata.address)
        elif isinstance(self.rdata, RDataCNAME):
            rdata_str = self.rdata.cname
        else:
            rdata_str = "UNKNOWN"

        return (
            f"name={self.name} "
            f"type={self.type.name} "
            f"class={self.class_.name} "
            f"ttl={self.ttl} "
            f"rdata={rdata_str}"
        )

    def to_logfmt(self, index: int) -> str:
        if isinstance(self.rdata, RDataA):
            rdata_str = str(self.rdata.address)
        elif isinstance(self.rdata, RDataCNAME):
            rdata_str = self.rdata.cname
        else:
            rdata_str = "UNKNOWN"

        return (
            f"answer.{index}.name={self.name} "
            f"answer.{index}.type={self.type.name} "
            f"answer.{index}.class={self.class_.name} "
            f"answer.{index}.ttl={self.ttl} "
            f"answer.{index}.rdata={rdata_str}"
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "DNSResourceRecord":
        offset = 0
        labels: List[str] = []
        while data[offset] != 0:
            length = data[offset]
            offset += 1
            labels.append(data[offset : offset + length].decode())
            offset += length
        name = ".".join(labels) + "."
        offset += 1

        type = Type(int.from_bytes(data[offset : offset + 2], "big"))
        class_ = Class(int.from_bytes(data[offset + 2 : offset + 4], "big"))
        ttl = int.from_bytes(data[offset + 4 : offset + 8], "big")
        rdlength = int.from_bytes(data[offset + 8 : offset + 10], "big")
        rdata_bytes = data[offset + 10 : offset + 10 + rdlength]
        rdata = RDataFactory.from_bytes(type, rdata_bytes)

        return cls(name=name, type=type, class_=class_, ttl=ttl, rdata=rdata)

    def to_bytes(self) -> bytes:
        name_bytes = encode_domain_name(self.name)
        type_bytes = self.type.value.to_bytes(2, "big")
        class_bytes = self.class_.value.to_bytes(2, "big")
        ttl_bytes = self.ttl.to_bytes(4, "big")
        rdata_bytes = self.rdata.to_bytes()
        rdlength_bytes = len(rdata_bytes).to_bytes(2, "big")

        return (
            name_bytes
            + type_bytes
            + class_bytes
            + ttl_bytes
            + rdlength_bytes
            + rdata_bytes
        )

    def byte_length(self) -> int:
        return len(self.to_bytes())
