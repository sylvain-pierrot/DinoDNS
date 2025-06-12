from parser import parse_dns_query
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
            header = parse_dns_query(raw)
            logger.info(f"Received request from {addr}: \n{header}")
            # response = build_dns_response(header, question, resolve_domain(question))
        except Exception as e:
            print(f"Error parsing/handling request from {addr}: {e}")
            return
