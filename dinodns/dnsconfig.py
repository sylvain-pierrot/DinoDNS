from dataclasses import dataclass
from typing import List, Optional
from dacite import Config, from_dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Record:
    name: str
    type: str
    value: str
    ttl: Optional[int]
    priority: Optional[int]


@dataclass
class Zone:
    zone: str
    origin: Optional[str]
    ttl: Optional[int]
    forward: Optional[List[str]]
    records: Optional[List[Record]]


@dataclass
class DnsConfig:
    zones: List[Zone]

    @classmethod
    def from_dict(cls, content: dict) -> "DnsConfig":
        return from_dict(
            data_class=DnsConfig,
            data=content,
            config=Config(strict=True, check_types=True),
        )
