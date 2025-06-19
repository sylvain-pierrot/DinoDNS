from ipaddress import IPv4Address
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Any, Optional
from dinodns.core.header import OpCode, RCode
from dinodns.core.message import DNSMessage
from dinodns.catalog import Catalog
from dinodns.core.question import QClass
from dinodns.resolver import try_resolve_query
import threading
import logging


logger = logging.getLogger(__name__)


class DinoDNS:
    def __init__(
        self,
        host: IPv4Address,
        port: int,
        catalog: Catalog,
        upstreams: list[IPv4Address] = [],
    ):
        self.host = host
        self.port = port
        self.catalog = catalog
        self.socket = socket(AF_INET, SOCK_DGRAM)
        self.upstreams = upstreams

    def start(self) -> None:
        logger.info(
            f'msg="Starting DNS server" host="{str(self.host)}" port={self.port}'
        )
        logger.info(
            f'msg="Using upstream forwarders" upstreams={[str(ip) for ip in self.upstreams]}'
        )

        self.socket.bind((str(self.host), self.port))
        logger.info(f'msg="Server listening on {self.host}:{self.port}"')

        while True:
            try:
                data, addr = self.socket.recvfrom(512)
                threading.Thread(
                    target=self.handle_client, args=(data, addr), daemon=True
                ).start()
            except KeyboardInterrupt:
                logger.info('msg="Shutting down"')
                break

    def handle_client(self, data: bytes, addr: Any) -> None:
        try:
            query = self.decode_query(data)
            response = self.handle_query(query)
            self.socket.sendto(response, addr)
        except Exception as e:
            logger.error(f'msg="Error handling client query: {e}" addr={addr}"')

    def decode_query(self, data: bytes) -> DNSMessage:
        return DNSMessage.from_bytes(data, 0)

    def handle_query(self, query: DNSMessage) -> bytes:
        if rcode := self.check_unsupported_features(query):
            query.header.flags.rcode = rcode
            return query.to_bytes()

        if not query.is_query():
            return query.to_bytes()

        return self.try_resolve_or_forward(query)

    def try_resolve_or_forward(self, query: DNSMessage) -> bytes:
        resolved = try_resolve_query(self.catalog, query)
        if resolved:
            return query.to_bytes()

        forwarded = self.forward_query(query)
        if forwarded:
            return forwarded

        query.header.flags.rcode = RCode.SERVFAIL
        return query.to_bytes()

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

        if message.header.qdcount != 1:
            logger.warning(
                f'msg="Only one question supported (QDCOUNT={message.header.qdcount})"'
            )
            return RCode.NOTIMP

        question = message.questions[0]
        if question.qclass != QClass.IN:
            logger.warning(f'msg="Unsupported QClass: {question.qclass.name}"')
            return RCode.NOTIMP

        return None

    def forward_query(self, query: DNSMessage, port: int = 53) -> Optional[bytes]:
        for upstream in self.upstreams:
            try:
                with socket(AF_INET, SOCK_DGRAM) as s:
                    s.settimeout(2)
                    s.sendto(query.to_bytes(), (str(upstream), port))
                    response_data, _ = s.recvfrom(512)
                    return response_data
            except Exception as e:
                logger.warning(
                    f'msg="Forwarding failed" upstream={upstream} error="{e}"'
                )
        return None
