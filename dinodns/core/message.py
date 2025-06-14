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
        questions = " ".join(
            self.questions[i].to_logfmt(i) for i in range(self.header.qdcount)
        )
        answers = " ".join(
            self.answers[i].to_logfmt(i) for i in range(self.header.ancount)
        )

        return f"kind=DNSMessage {self.header} {questions} {answers}"

    @classmethod
    def from_bytes(cls, data: bytes) -> "DNSMessage":
        if len(data) > 512:
            raise ValueError("DNS message exceeds maximum length of 512 bytes")

        offset = 12
        header = DNSHeader.from_bytes(data[:offset])
        questions = []
        for _ in range(header.qdcount):
            question = DNSQuestion.from_bytes(data[offset:])
            offset += question.byte_length()
            questions.append(question)
        answers = []
        for _ in range(header.ancount):
            answer = DNSAnswer.from_bytes(data[offset:])
            offset += answer.byte_length()
            answers.append(answer)
        authorities = []

        return cls(
            header=header,
            questions=questions,
            answers=answers,
            authorities=authorities,
            additional=[],
        )

    def to_bytes(self) -> bytes:
        data = self.header.to_bytes()
        for q in self.questions:
            data += q.to_bytes()
        for a in self.answers:
            data += a.to_bytes()
        return data
