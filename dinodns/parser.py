from question import DNSQuestion
from message import DNSMessage
from header import DNSHeader
import logging

logger = logging.getLogger(__name__)


def parse_dns_query(raw: bytes) -> DNSMessage:
    if len(raw) > 512:
        raise ValueError("DNS message exceeds maximum length of 512 bytes")

    # Headers are always 12 bytes long
    offset = 12
    header = DNSHeader(raw[:offset])
    message = DNSMessage(
        header=header,
        question=[],
        response=[],
        authority=[],
        additional=[],
    )

    for _ in range(header.qdcount):
        question = DNSQuestion(raw[offset:])
        offset += question.byte_length()
        message.question.append(question)

    return message
