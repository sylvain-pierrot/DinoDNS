from dataclasses import dataclass
from typing import List
from dinodns.core.rr.resource_record import DNSResourceRecord
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
    def from_bytes(cls, data: bytes, offset: int) -> "DNSMessage":
        if len(data) > 512:
            raise ValueError("DNS message exceeds maximum length of 512 bytes")

        header = DNSHeader.from_bytes(data, offset)
        offset += header.byte_length()

        questions: List[DNSQuestion] = []
        for _ in range(header.qdcount):
            question = DNSQuestion.from_bytes(data, offset)
            offset += question.byte_length()
            questions.append(question)

        answers: List[DNSResourceRecord] = []
        for _ in range(header.ancount):
            rr = DNSResourceRecord.from_bytes(data, offset)
            offset += rr.byte_length()
            answers.append(rr)

        authorities: List[DNSResourceRecord] = []
        for _ in range(header.nscount):
            rr = DNSResourceRecord.from_bytes(data, offset)
            offset += rr.byte_length()
            authorities.append(rr)

        additional: List[DNSResourceRecord] = []
        for _ in range(header.arcount):
            rr = DNSResourceRecord.from_bytes(data, offset)
            offset += rr.byte_length()
            additional.append(rr)

        return cls(
            header=header,
            questions=questions,
            answers=answers,
            authorities=authorities,
            additional=additional,
        )

    def to_bytes(self) -> bytes:
        data = self.header.to_bytes()

        for question in self.questions:
            data += question.to_bytes()

        for i in range(self.header.ancount):
            data += self.answers[i].to_bytes()

        for i in range(self.header.nscount):
            data += self.authorities[i].to_bytes()

        for i in range(self.header.arcount):
            data += self.additional[i].to_bytes()

        return data

    def is_query(self) -> bool:
        return self.header.flags.qr == 0

    def promote_to_response(self, recursion_supported: bool) -> None:
        self.header.flags.qr = 1
        self.header.flags.ra = int(recursion_supported)

    def set_answers(self, answers: list["DNSResourceRecord"]) -> None:
        self.answers.extend(answers)
        self.header.ancount += len(answers)

    def set_additional(self, additional: list["DNSResourceRecord"]) -> None:
        self.additional.extend(additional)
        self.header.arcount += len(additional)
