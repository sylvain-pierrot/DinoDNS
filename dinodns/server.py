from ipaddress import IPv4Address
from socket import AF_INET, SOCK_DGRAM, socket
from typing import Optional
from dinodns.core.header import OpCode, RCode
from dinodns.core.message import DNSMessage
from dinodns.catalog import Catalog
from dinodns.core.question import QClass
from dinodns.resolver import try_resolve_query
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
                query = self.decode_query(data)
                response = self.handle_query(query)
                self.socket.sendto(response.to_bytes(), addr)
            except KeyboardInterrupt:
                logger.info('msg="Shutting down"')
                break
            except Exception as e:
                logger.error(f'msg="Error handling query: {e}"')
                continue

    def decode_query(self, data: bytes) -> DNSMessage:
        return DNSMessage.from_bytes(data, 0)

    def handle_query(self, query: DNSMessage) -> DNSMessage:
        rcode = DinoDNS.check_unsupported_features(query)
        if rcode:
            query.header.flags.rcode = rcode
            return query

        if not query.is_query():
            return query

        resolved = try_resolve_query(self.catalog, query)
        if resolved:
            logger.info(query)
            return query

        forwarded = self.forward_query(query)
        if forwarded:
            logger.info(query)
            return forwarded

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

    def forward_query(self, query: DNSMessage, port: int = 53) -> Optional[DNSMessage]:
        raw_query = query.to_bytes()
        for upstream in self.upstreams:
            try:
                with socket(AF_INET, SOCK_DGRAM) as s:
                    s.settimeout(2)  # Sécurité pour ne pas bloquer
                    s.sendto(raw_query, (str(upstream), port))
                    response_data, _ = s.recvfrom(512)
                    return DNSMessage.from_bytes(response_data, 0)
            except Exception as e:
                logger.warning(
                    f'msg="Forwarding failed" upstreams={self.upstreams} error="{e}"'
                )
                query.header.flags.rcode = RCode.SERVFAIL
        return None
