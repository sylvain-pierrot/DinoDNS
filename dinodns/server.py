from dinodns.core.answer import DNSAnswer
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Tuple
import logging

from dinodns.core.message import DNSMessage

logger = logging.getLogger(__name__)


class DinoDNS:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start(self) -> None:
        self.socket.bind((self.host, self.port))
        logger.info(f"Server listening on {self.host}:{self.port}")
        while True:
            try:
                data, addr = self.socket.recvfrom(512)
                self.handle_request(data, addr)
            except KeyboardInterrupt:
                logger.info("Shutting down.")
                break

    def handle_request(self, data: bytes, addr: Tuple[str, int]) -> None:
        try:
            query = DNSMessage.from_bytes(data)
            logger.info(f"Received request from {addr}: \n{query}")

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

            self.socket.sendto(query.to_bytes(), addr)
            logger.info(f"Sending response to {addr}: \n{query}")

        except Exception as e:
            print(f"Error parsing/handling request from {addr}: {e}")
            return
