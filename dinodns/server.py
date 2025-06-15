from socket import AF_INET, SOCK_DGRAM, socket
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
        if not query.is_query():
            return query

        query.promote_to_response(recursion_supported=False)

        rcode = query.check_unsupported_features()
        if rcode:
            query.header.flags.rcode = rcode
            return query

        try_resolve_query(self.catalog, query)

        return query
