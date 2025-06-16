from dataclasses import dataclass
from dinodns.catalog import NSRecord, Record
from dinodns.core.rr.rdata.base import RData, register_rdata
from dinodns.core.rr.types import Type
from dinodns.utils import decode_domain_name, encode_domain_name


@register_rdata
@dataclass
class RDataNS(RData):
    nsdname: str

    @property
    def domain_name_target(self) -> str:
        return self.nsdname

    @classmethod
    def from_bytes(cls, data: bytes) -> "RDataNS":
        return cls(nsdname=decode_domain_name(data)[0])

    def to_bytes(self) -> bytes:
        return encode_domain_name(self.nsdname)

    @classmethod
    def rr_type(cls) -> Type:
        return Type.NS

    @classmethod
    def from_record(cls, record: Record) -> "RDataNS":
        if not isinstance(record, NSRecord):
            raise TypeError(f"Expected NSRecord, got {type(record).__name__}")
        return cls(nsdname=record.nsdname)

    @classmethod
    def requires_glue_record(cls) -> bool:
        return True
