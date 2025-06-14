from socket import AF_INET, SOCK_DGRAM, socket
from dinodns.core.answer import DNSAnswer
from dinodns.core.header import OpCode
from dinodns.core.message import DNSMessage
from dinodns.catalog import Catalog
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
        logger.info(f"Server listening on {self.host}:{self.port}")

        while True:
            try:
                data, addr = self.socket.recvfrom(512)
                query = self.decode_query(data)
                logger.info(f"Received query from {addr}")
                response = self.handle_query(query)

                self.socket.sendto(response.to_bytes(), addr)
                logger.info(f"Sending response to {addr}")
            except KeyboardInterrupt:
                logger.info("Shutting down.")
                break
            except Exception as e:
                logger.error(f"Error handling query: {e}")
                break

    def decode_query(self, data: bytes) -> DNSMessage:
        query = DNSMessage.from_bytes(data)
        logger.debug(f"Decode query: \n{query}")
        return query

    def handle_query(self, query: DNSMessage) -> DNSMessage:
        if query.header.flags.qr == 0:
            query.header.flags.qr = 1
            query.header.flags.ra = 0

            if query.header.flags.tc:
                logger.warning(
                    "Truncated response, not supported in this implementation."
                )
                query.header.flags.rcode = 5
            else:
                match query.header.flags.opcode:
                    case OpCode.QUERY:
                        logger.debug("Handling standard query")
                        for i in range(query.header.qdcount):
                            question = query.questions[i]
                            record = self.catalog.search(question)
                            if record is None:
                                logger.warning(f"No record found for {question.qname}")
                                query.header.flags.rcode = 3
                            else:
                                answer = DNSAnswer(
                                    query.questions[i].qname,
                                    query.questions[i].qtype,
                                    query.questions[i].qclass,
                                    record.ttl,
                                    record.get_rdata(),
                                )
                                query.answers.append(answer)
                                query.header.ancount += 1
                                query.header.flags.rcode = 0
                                query.header.flags.aa = 1
                    case _:
                        logger.warning(
                            f"Unsupported OpCode: {query.header.flags.opcode}"
                        )
                        query.header.flags.rcode = 4
        return query
