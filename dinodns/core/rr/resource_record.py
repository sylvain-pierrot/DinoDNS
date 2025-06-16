from dataclasses import dataclass
from typing import List
from dinodns.catalog import Record
from dinodns.core.rr.classes import Class
from dinodns.core.rr.rdata.base import RData, RDataFactory
from dinodns.core.rr.types import Type
from dinodns.utils import encode_domain_name
import logging

logger = logging.getLogger(__name__)


@dataclass
class DNSResourceRecord:
    name: str
    type: Type
    class_: Class
    ttl: int
    rdata: RData

    def __str__(self) -> str:
        return (
            f"name={self.name} "
            f"type={self.type.name} "
            f"class={self.class_.name} "
            f"ttl={self.ttl} "
            f"rdata={self.rdata}"
        )

    def to_logfmt(self, index: int) -> str:
        return (
            f"answer.{index}.name={self.name} "
            f"answer.{index}.type={self.type.name} "
            f"answer.{index}.class={self.class_.name} "
            f"answer.{index}.ttl={self.ttl} "
            f"answer.{index}.rdata={self.rdata}"
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

    @classmethod
    def from_record(cls, record: Record) -> "DNSResourceRecord":
        rdata = RDataFactory.from_record(record)
        return cls(
            name=record.domain_name,
            type=Type[record.type],
            class_=Class[record.class_],
            ttl=record.ttl,
            rdata=rdata,
        )

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

    def requires_glue_record(self) -> bool:
        return self.rdata.requires_glue_record()
