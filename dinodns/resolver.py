from ipaddress import IPv4Address
from typing import Optional
from dinodns.catalog import Catalog, ARecord
from dinodns.core.question import DNSQuestion
from dinodns.core.resource_record import (
    Class,
    DNSResourceRecord,
    RDataA,
    RDataCNAME,
    Type,
)
import logging

logger = logging.getLogger(__name__)


def try_resolve_question(
    catalog: Catalog, question: DNSQuestion
) -> "Optional[DNSResourceRecord]":
    record = catalog.try_lookup_record(question)

    if record is None:
        logger.warning(f'msg="No record found for {question.qname}"')
        return None

    if isinstance(record, ARecord):
        rdata = RDataA(address=IPv4Address(record.host_address))
    else:
        rdata = RDataCNAME(cname=record.cname)

    logger.info("teeeesssstttt 1")
    return DNSResourceRecord(
        name=question.qname,
        type=Type(question.qtype.value),
        class_=Class(question.qclass.value),
        ttl=record.ttl,
        rdata=rdata,
    )
