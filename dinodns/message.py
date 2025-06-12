from dataclasses import dataclass
from typing import List
from header import DNSHeader
from question import DNSQuestion
import logging

logger = logging.getLogger(__name__)


@dataclass
class DNSResponse:
    pass


@dataclass
class DNSAuthority:
    pass


@dataclass
class DNSAdditional:
    pass


@dataclass
class DNSMessage:
    header: DNSHeader
    question: List[DNSQuestion]
    response: List[DNSResponse]
    authority: List[DNSAuthority]
    additional: List[DNSAdditional]

    def __str__(self) -> str:
        return self.header.__str__()
