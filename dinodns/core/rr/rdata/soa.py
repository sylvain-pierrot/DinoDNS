from dataclasses import dataclass
from dinodns.catalog import SOARecord, Record
from dinodns.core.rr.rdata.base import RData, register_rdata
from dinodns.core.rr.types import Type
from dinodns.utils import (
    decode_domain_name,
    decode_email,
    encode_domain_name,
    encode_email,
)


@register_rdata
@dataclass
class RDataSOA(RData):
    mname: str  # Primary master name server
    rname: str  # Responsible person's email
    serial: int
    refresh: int
    retry: int
    expire: int
    minimum: int

    @classmethod
    def from_bytes(cls, data: bytes) -> "RDataSOA":
        offset = 0

        mname, mname_len = decode_domain_name(data)
        offset += mname_len
        rname, rname_len = decode_email(data[offset:])
        offset += rname_len
        serial = int.from_bytes(data[offset : offset + 4], "big")
        refresh = int.from_bytes(data[offset + 4 : offset + 8], "big")
        retry = int.from_bytes(data[offset + 8 : offset + 12], "big")
        expire = int.from_bytes(data[offset + 12 : offset + 16], "big")
        minimum = int.from_bytes(data[offset + 16 : offset + 20], "big")

        return cls(mname, rname, serial, refresh, retry, expire, minimum)

    def to_bytes(self) -> bytes:
        return (
            encode_domain_name(self.mname)
            + encode_email(self.rname)
            + self.serial.to_bytes(4, "big")
            + self.refresh.to_bytes(4, "big")
            + self.retry.to_bytes(4, "big")
            + self.expire.to_bytes(4, "big")
            + self.minimum.to_bytes(4, "big")
        )

    @classmethod
    def rr_type(cls) -> Type:
        return Type.SOA

    @classmethod
    def from_record(cls, record: Record) -> "RDataSOA":
        if not isinstance(record, SOARecord):
            raise TypeError(f"Expected SOARecord, got {type(record).__name__}")
        return cls(
            mname=record.mname,
            rname=record.rname,
            serial=record.serial,
            refresh=record.refresh,
            retry=record.retry,
            expire=record.expire,
            minimum=record.minimum,
        )

    @classmethod
    def requires_glue_record(cls) -> bool:
        return False
