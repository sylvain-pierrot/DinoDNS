from dataclasses import dataclass


@dataclass
class DNSAnswer:
    name: bytes
    type: bytes
    class_: bytes
    ttl: int
    rdata: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> "DNSAnswer":
        null_label_index = data.index(b"\x00") + 1

        name = data[:null_label_index]
        type_ = data[null_label_index : null_label_index + 2]
        class_ = data[null_label_index + 2 : null_label_index + 4]
        ttl = int.from_bytes(data[null_label_index + 4 : null_label_index + 8], "big")
        rdlength = int.from_bytes(
            data[null_label_index + 8 : null_label_index + 10], "big"
        )
        rdata = data[null_label_index + 10 : null_label_index + 10 + rdlength]

        return cls(name=name, type=type_, class_=class_, ttl=ttl, rdata=rdata)

    def byte_length(self) -> int:
        return (
            len(self.name)
            + len(self.type)
            + len(self.class_)
            + 4  # TTL is 4 bytes
            + 2  # RDLength is 2 bytes
            + len(self.rdata)
        )

    def to_bytes(self) -> bytes:
        return (
            self.name
            + self.type
            + self.class_
            + self.ttl.to_bytes(4, "big")
            + len(self.rdata).to_bytes(2, "big")
            + self.rdata
        )
