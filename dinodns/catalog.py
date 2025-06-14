from dataclasses import dataclass
from dinodns.core.question import DNSQuestion
from dinodns.utils import convert_keys
from typing import List, Union, Literal
from click import Path
import click
import dacite
import logging
import tomllib


logger = logging.getLogger(__name__)


@dataclass
class ARecord:
    domain_name: str
    ttl: int
    class_: Literal["IN"]
    type: Literal["A"]
    host_address: str

    def get_rdata(self) -> bytes:
        parts = self.host_address.split(".")
        if len(parts) != 4:
            raise ValueError(f"Invalid IPv4 address: {self.host_address}")
        return bytes(int(part) for part in parts)


@dataclass
class CNAMERecord:
    domain_name: str
    ttl: int
    class_: Literal["IN"]
    type: Literal["CNAME"]
    cname: str

    def get_rdata(self) -> bytes:
        return self.cname.encode("utf-8") + b"\x00"


@dataclass
class Zone:
    origin: str
    records: List[Union[ARecord, CNAMERecord]]


@dataclass
class Catalog:
    zones: List[Zone]

    def __str__(self):
        lines = []
        for zone in self.zones:
            lines.append(f"Zone: {zone.origin}")
            for record in zone.records:
                rdata = getattr(record, "host_address", None) or getattr(
                    record, "cname", ""
                )
                lines.append(
                    f"      {record.domain_name:<15} {record.ttl:<5} {record.class_:<3} {record.type:<6} {rdata}"
                )
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def from_file(cls, file_path: Path) -> "Catalog":
        content = tomllib.load(click.open_file(click.format_filename(file_path), "rb"))
        converted = convert_keys(content)
        catalog = dacite.from_dict(
            data_class=Catalog,
            data=converted,
            config=dacite.Config(
                strict=True, strict_unions_match=True, check_types=True
            ),
        )
        return catalog

    def search(self, question: DNSQuestion) -> Union[ARecord, CNAMERecord]:
        for zone in self.zones:
            if question.get_label_name().endswith(zone.origin):
                for record in zone.records:
                    domaine_name = (
                        zone.origin if record.domain_name == "@" else record.domain_name
                    )
                    if domaine_name == question.get_label_name():
                        return record
        raise ValueError(f"No record found for {question.qname}")
