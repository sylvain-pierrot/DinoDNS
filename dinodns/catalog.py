from dataclasses import dataclass
from dinodns.core.question import DNSQuestion
from dinodns.utils import convert_keys
from typing import List, Optional, Union, Literal
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


@dataclass
class CNAMERecord:
    domain_name: str
    ttl: int
    class_: Literal["IN"]
    type: Literal["CNAME"]
    cname: str


@dataclass
class NSRecord:
    domain_name: str
    ttl: int
    class_: Literal["IN"]
    type: Literal["NS"]
    nsdname: str


Record = Union[ARecord, CNAMERecord, NSRecord]


@dataclass
class Zone:
    origin: str
    records: List[Record]


@dataclass
class Catalog:
    zones: List[Zone]

    def __str__(self) -> str:
        entries: List[str] = []
        for i, zone in enumerate(self.zones):
            entries.append(
                f"zone.{i}.origin={zone.origin} zone.{i}.records={len(zone.records)}"
            )
        return " ".join(entries)

    def master_format(self) -> str:
        lines: List[str] = []
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
        content = tomllib.load(
            click.open_file(click.format_filename(str(file_path)), "rb")
        )
        converted = convert_keys(content)
        catalog = dacite.from_dict(
            data_class=Catalog,
            data=converted,
            config=dacite.Config(
                strict=True, strict_unions_match=True, check_types=True
            ),
        )
        return catalog

    def try_lookup_record(self, question: DNSQuestion) -> Optional[Record]:
        qname = question.qname.rstrip(".").lower()

        for zone in self.zones:
            origin = zone.origin.rstrip(".").lower()

            if not qname.endswith(origin):
                continue

            for record in zone.records:
                record_relative = record.domain_name.rstrip(".").lower()
                record_fqdn = (
                    origin if record_relative == "@" else f"{record_relative}.{origin}"
                )

                if (
                    record_fqdn == qname
                    and question.qtype.name == record.type
                    and question.qclass.name == record.class_
                ):
                    return record

        return None
