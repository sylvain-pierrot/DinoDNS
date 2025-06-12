from dataclasses import dataclass
from typing import List
from dinodns.core.answer import DNSAnswer
from dinodns.core.header import DNSHeader
from dinodns.core.question import DNSQuestion
import logging

logger = logging.getLogger(__name__)


@dataclass
class DNSAuthority:
    pass


@dataclass
class DNSAdditional:
    pass


@dataclass
class DNSMessage:
    header: DNSHeader
    questions: List[DNSQuestion]
    answers: List[DNSAnswer]
    authorities: List[DNSAuthority]
    additional: List[DNSAdditional]

    def __str__(self) -> str:
        return self.header.__str__()

    def to_bytes(self) -> bytes:
        raw = self.header.to_bytes()
        for q in self.questions:
            raw += q.to_bytes()
        for a in self.answers:
            raw += a.to_bytes()
        return raw
