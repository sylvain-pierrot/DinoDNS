from dataclasses import dataclass
from typing import List, Optional
from dinodns.core.rr.resource_record import DNSResourceRecord
from dinodns.core.header import DNSHeader, OpCode, RCode
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
        questions: List[DNSQuestion] = []
        for _ in range(header.qdcount):
            question = DNSQuestion.from_bytes(data[offset:])
            offset += question.byte_length()
            questions.append(question)
        answers: List[DNSResourceRecord] = []
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
        for question in self.questions:
            data += question.to_bytes()
        for answer in self.answers:
            data += answer.to_bytes()
        for a in self.additional:
            data += a.to_bytes()
        return data

    def is_query(self) -> bool:
        return self.header.flags.qr == 0

    def promote_to_response(self, recursion_supported: bool) -> None:
        self.header.flags.qr = 1
        self.header.flags.ra = int(recursion_supported)

    def check_unsupported_features(self) -> Optional[RCode]:
        if self.header.flags.tc:
            logger.warning('msg="Truncated flag set: not supported"')
            return RCode.REFUSED

        if self.header.flags.opcode != OpCode.QUERY:
            logger.warning(f'msg="Unsupported OpCode: {self.header.flags.opcode.name}"')
            return RCode.NOTIMP

        if self.header.flags.z != 0:
            logger.warning('msg="Z flag must be zero (reserved)"')
            return RCode.FORMERR

        if self.header.flags.qr == 0 and self.header.qdcount != 1:
            logger.warning(
                f'msg="Only one question supported (QDCOUNT={self.header.qdcount})"'
            )
            return RCode.NOTIMP

        return None

    def set_answers(self, answers: list["DNSResourceRecord"]) -> None:
        self.answers = answers
        self.header.ancount = len(answers)

    def set_additional(self, additional: list["DNSResourceRecord"]) -> None:
        self.additional = additional
        self.header.arcount = len(additional)
