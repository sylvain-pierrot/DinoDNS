from abc import ABC, abstractmethod
from ipaddress import IPv4Address
from typing import Optional, Type
from dinodns.catalog import ARecord, Catalog
from dinodns.core.question import DNSQuestion, QClass, QType
from dataclasses import dataclass
from dinodns.utils import decode_domain_name, encode_domain_name
import logging

logger = logging.getLogger(__name__)


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


class RDataFactory:
    _registry: dict[QType, RData] = {
        QType.A: RDataA,
        QType.CNAME: RDataCNAME,
    }

    @staticmethod
    def from_bytes(qtype: QType, data: bytes) -> RData:
        cls = RDataFactory._registry.get(qtype)
        if cls is None:
            raise NotImplementedError(f"Unsupported QType: {qtype}")
        return cls.from_bytes(data)


@dataclass
class DNSAnswer:
    name: str
    type: QType
    class_: QClass
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
    def from_bytes(cls, data: bytes) -> "DNSAnswer":
        offset = 0
        labels = []
        while data[offset] != 0:
            length = data[offset]
            offset += 1
            labels.append(data[offset : offset + length].decode())
            offset += length
        name = ".".join(labels) + "."
        offset += 1

        type = QType(int.from_bytes(data[offset : offset + 2], "big"))
        class_ = QClass(int.from_bytes(data[offset + 2 : offset + 4], "big"))
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

    @classmethod
    def try_answer(
        clc, catalog: Catalog, question: DNSQuestion
    ) -> "Optional[DNSAnswer]":
        record = catalog.try_lookup_record(question)

        if record is None:
            logger.warning(f'msg="No record found for {question.qname}"')
            return None

        if isinstance(record, ARecord):
            rdata = RDataA(address=IPv4Address(record.host_address))
        else:
            rdata = RDataCNAME(cname=record.cname)

        return DNSAnswer(
            name=question.qname,
            type=question.qtype,
            class_=question.qclass,
            ttl=record.ttl,
            rdata=rdata,
        )
