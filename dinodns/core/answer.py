from dataclasses import dataclass


@dataclass
class DNSAnswer:
    name: bytes
    type: bytes
    class_: bytes
    ttl: int
    rdata: bytes

    def to_bytes(self) -> bytes:
        raw = self.name + self.type + self.class_ + self.ttl.to_bytes(4, "big")
        rdlength = len(self.rdata).to_bytes(2, "big")
        return raw + rdlength + self.rdata
