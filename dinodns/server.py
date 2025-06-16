from socket import AF_INET, SOCK_DGRAM, socket
from typing import Optional
from dinodns.core.header import OpCode, RCode
from dinodns.core.message import DNSMessage
from dinodns.catalog import Catalog
from dinodns.resolver import try_resolve_query
import logging


logger = logging.getLogger(__name__)


class DinoDNS:
    def __init__(self, host: str, port: int, catalog: Catalog):
        self.host = host
        self.port = port
        self.catalog = catalog
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start(self) -> None:
        self.socket.bind((self.host, self.port))
        logger.info(f'msg="Server listening on {self.host}:{self.port}"')

        while True:
            try:
                data, addr = self.socket.recvfrom(512)
                query = self.decode_query(data)
                logger.info(
                    f'msg="DNS query intercepted from {addr[0]}:{addr[1]}" kind=DNSMessage {query}'
                )
                response = self.handle_query(query)
                self.socket.sendto(response.to_bytes(), addr)
            except KeyboardInterrupt:
                logger.info('msg="Shutting down"')
                break
            except Exception as e:
                logger.error(f'msg="Error handling query: {e}"')
                break

    def decode_query(self, data: bytes) -> DNSMessage:
        return DNSMessage.from_bytes(data)

    def handle_query(self, query: DNSMessage) -> DNSMessage:
        rcode = DinoDNS.check_unsupported_features(query)
        if rcode:
            query.header.flags.rcode = rcode
            return query

        if not query.is_query():
            return query

        query.promote_to_response(recursion_supported=False)
        try_resolve_query(self.catalog, query)

        return query

    @staticmethod
    def check_unsupported_features(message: DNSMessage) -> Optional[RCode]:
        if message.header.flags.tc:
            logger.warning('msg="Truncated flag set: not supported"')
            return RCode.REFUSED

        if message.header.flags.opcode != OpCode.QUERY:
            logger.warning(
                f'msg="Unsupported OpCode: {message.header.flags.opcode.name}"'
            )
            return RCode.NOTIMP

        if message.header.flags.z != 0:
            logger.warning('msg="Z flag must be zero (reserved)"')
            return RCode.FORMERR

        if message.header.flags.qr == 0 and message.header.qdcount != 1:
            logger.warning(
                f'msg="Only one question supported (QDCOUNT={message.header.qdcount})"'
            )
            return RCode.NOTIMP

        return None
