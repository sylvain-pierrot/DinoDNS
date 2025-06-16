from dataclasses import dataclass
from ipaddress import IPv4Address
from dinodns.catalog import ARecord, Record
from dinodns.core.rr.rdata.base import RData, register_rdata
from dinodns.core.rr.types import Type


@register_rdata
@dataclass
class RDataA(RData):
    address: IPv4Address

    @classmethod
    def from_bytes(cls, data: bytes) -> "RDataA":
        if len(data) != 4:
            raise ValueError(f"Invalid IPv4 address length: {len(data)} bytes")
        return cls(address=IPv4Address(data))

    def to_bytes(self) -> bytes:
        return self.address.packed

    @classmethod
    def rr_type(cls) -> Type:
        return Type.A

    @classmethod
    def from_record(cls, record: Record) -> "RDataA":
        if not isinstance(record, ARecord):
            raise TypeError(f"Expected ARecord, got {type(record).__name__}")
        return cls(address=IPv4Address(record.host_address))
