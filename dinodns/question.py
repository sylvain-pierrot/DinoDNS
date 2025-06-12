from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class QType(Enum):
    A = 1
    NS = 2
    CNAME = 5
    SOA = 6
    PTR = 12
    MX = 15
    TXT = 16
    AAAA = 28
    SRV = 33


class QClass(Enum):
    IN = 1  # Internet class
    CS = 2  # CSNET class (obsolete)
    CH = 3  # CHAOS class (obsolete)
    HS = 4  # Hesiod class (obsolete)


@dataclass
class DNSQuestion:
    qname: bytes
    qtype: bytes
    qclass: bytes

    def __init__(self, raw_from_question: bytes):
        null_label_index = raw_from_question.index(b"\x00") + 1

        self.qname = raw_from_question[:null_label_index]
        self.qtype = raw_from_question[null_label_index : null_label_index + 2]
        self.qclass = raw_from_question[null_label_index + 2 : null_label_index + 4]
        # self.qclass = 1  # Defaulting to IN (Internet) class

    def byte_length(self) -> int:
        return len(self.qname) + 2 + 2

    def get_type(self) -> QType:
        try:
            return QType(int.from_bytes(self.qtype, "big"))
        except ValueError:
            logger.error(f"Unknown record type: {self.qtype}")
            return None

    def get_class(self) -> QClass:
        try:
            return QClass(int.from_bytes(self.qclass, "big"))
        except ValueError:
            logger.error(f"Unknown class type: {self.qclass}")
            return None

    def get_label_name(self) -> str:
        labels = []
        offset = 0

        while True:
            label_length = self.qname[offset]
            if label_length == 0:
                break

            offset += 1
            label = self.qname[offset : offset + label_length]
            labels.append(label.decode())
            offset += label_length

        return ".".join(labels) + "."
