from dataclasses import dataclass
from typing import List
import logging
logger = logging.getLogger(__name__)

@dataclass
class Flags:
    qr: int
    opcode: int
    aa: int
    tc: int
    rd: int
    ra: int
    zero: int
    rcode: int

@dataclass 
class Header:
    id: int
    flags: Flags
    question_count: int
    answer_rr_count: int
    authority_rr_count: int
    additional_rr_count: int

@dataclass
class DNSMessage:
    header: Header
    question: List[int]
    response: List[int]
    authority: List[int]
    additional: List[int]

def parse_dns_query(data: bytes) -> Header:
    if(len(data) > 512):
        raise ValueError("DNS message exceeds maximum length of 512 bytes")
    
    raw_header = data[:12]
    flags_int = int.from_bytes(raw_header[2:4], byteorder='big') 

    header = Header(
        id=int.from_bytes(raw_header[:2]),
        flags=Flags(
            qr=(flags_int >> 15) & 0x1,
            opcode=(flags_int >> 11) & 0xF,
            aa=(flags_int >> 10) & 0x1,
            tc=(flags_int >> 9) & 0x1,
            rd=(flags_int >> 8) & 0x1,
            ra=(flags_int >> 7) & 0x1,
            zero=(flags_int >> 4) & 0x7,
            rcode=flags_int & 0xF
        ),
        question_count=int.from_bytes(raw_header[4:6]),
        answer_rr_count=int.from_bytes(raw_header[6:8]),
        authority_rr_count=int.from_bytes(raw_header[8:10]),
        additional_rr_count=int.from_bytes(raw_header[10:12])
    )

    logger.info(f"Parsed DNS header: {header}")

    return header

