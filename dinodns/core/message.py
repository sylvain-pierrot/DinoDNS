from dataclasses import dataclass
from typing import List
from dinodns.core.resource_record import DNSResourceRecord
from dinodns.core.header import DNSHeader
from dinodns.core.question import DNSQuestion
import logging

logger = logging.getLogger(__name__)


@dataclass
class DNSMessage:
    header: DNSHeader
    questions: List[DNSQuestion]
    answers: List[DNSResourceRecord]
    authorities: List[DNSResourceRecord]
    additional: List[DNSResourceRecord]

    def __str__(self) -> str:
        questions = " ".join(
            self.questions[i].to_logfmt(i) for i in range(self.header.qdcount)
        )
        answers = " ".join(
            self.answers[i].to_logfmt(i) for i in range(self.header.ancount)
        )

        return f"{self.header} {questions} {answers}"

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
            answer = DNSResourceRecord.from_bytes(data[offset:])
            offset += answer.byte_length()
            answers.append(answer)

        return cls(
            header=header,
            questions=questions,
            answers=answers,
            authorities=[],
            additional=[],
        )

    def to_bytes(self) -> bytes:
        data = self.header.to_bytes()
        for q in self.questions:
            data += q.to_bytes()
        for a in self.answers:
            data += a.to_bytes()
        return data
