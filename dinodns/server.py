from dinodns.core.answer import DNSAnswer
from dinodns.parser import parse_dns_query
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


class DinoDNS:
    def __init__(self, host: str = "0.0.0.0", port: int = 53) -> None:
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start(self) -> None:
        self.socket.bind((self.host, self.port))
        logger.info(f"Server listening on {self.host}:{self.port}")
        while True:
            try:
                raw, addr = self.socket.recvfrom(512)
                self.handle_request(raw, addr)
            except KeyboardInterrupt:
                logger.info("Shutting down.")
                break

    def handle_request(self, raw: bytes, addr: Tuple[str, int]) -> None:
        try:
            query = parse_dns_query(raw)
            logger.info(f"Received request from {addr}: \n{query}")
            logger.info(
                f"DNS query for {query.questions[0].get_label_name()} of type {query.questions[0].get_type().name} at {query.questions[0].get_class().name}"
            )

            query.header.flags.qr = 1
            query.header.flags.ra = 1

            answer = DNSAnswer(
                query.questions[0].qname,
                query.questions[0].qtype,
                query.questions[0].qclass,
                30,
                bytes([127, 0, 0, 1]),
            )
            query.answers.append(answer)
            query.header.ancount += 1
            logger.info(f"Sending response to {addr}: \n{query.to_bytes()}")
            self.socket.sendto(query.to_bytes(), addr)

        except Exception as e:
            print(f"Error parsing/handling request from {addr}: {e}")
            return
