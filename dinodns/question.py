from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


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

    def byte_length(self) -> int:
        return len(self.qname) + 2 + 2

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
