from dataclasses import dataclass
from dinodns.catalog import CNAMERecord, Record
from dinodns.core.rr.rdata.base import RData, register_rdata
from dinodns.core.rr.types import Type
from dinodns.utils import decode_domain_name, encode_domain_name


@register_rdata
@dataclass
class RDataCNAME(RData):
    cname: str

    @property
    def domain_name_target(self) -> str:
        return self.cname

    @classmethod
    def from_bytes(cls, data: bytes) -> "RDataCNAME":
        return cls(cname=decode_domain_name(data)[0])

    def to_bytes(self) -> bytes:
        return encode_domain_name(self.cname)

    @classmethod
    def rr_type(cls) -> Type:
        return Type.CNAME

    @classmethod
    def from_record(cls, record: Record) -> "RDataCNAME":
        if not isinstance(record, CNAMERecord):
            raise TypeError(f"Expected CNAMERecord, got {type(record).__name__}")
        return cls(cname=record.cname)

    @classmethod
    def requires_glue_record(cls) -> bool:
        return True
