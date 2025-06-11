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
        logger.info(f"[DNS] Server listening on {self.host}:{self.port}")
        while True:
            try:
                data, addr = self.socket.recvfrom(512)
                self.handle_request(data, addr)
            except KeyboardInterrupt:
                logger.info("[DNS] Shutting down.")
                break
    
    def handle_request(self, data: bytes, addr: Tuple[str, int]) -> None:
        try:
            header = parse_dns_query(data)
            logger.info(f"[DNS] Received request from {addr}: {header}")
            # response = build_dns_response(header, question, resolve_domain(question))
        except Exception as e:
            print(f"[DNS] Error parsing/handling request from {addr}: {e}")
            return
