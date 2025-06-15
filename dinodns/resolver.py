from ipaddress import IPv4Address
from typing import List, Optional
from dinodns.catalog import Catalog, ARecord
from dinodns.core.message import DNSMessage
from dinodns.core.question import DNSQuestion, QClass, QType
from dinodns.core.resource_record import (
    Class,
    DNSResourceRecord,
    RDataA,
    RDataCNAME,
    RDataNS,
    Type,
)
import logging

logger = logging.getLogger(__name__)


def try_resolve_query(catalog: Catalog, query: DNSMessage) -> "Optional[DNSMessage]":
    question = query.questions[0]

    if question.qclass != QClass.IN:
        return None

    record = catalog.try_lookup_record(question)
    if record is None:
        logger.warning(f'msg="No record found for {question.qname}"')
        return None

    answers: List[DNSResourceRecord] = []
    additional: List[DNSResourceRecord] = []

    if question.qtype == QType.A and hasattr(record, "host_address"):
        rdata = RDataA(address=IPv4Address(record.host_address))
        rr = DNSResourceRecord(
            name=question.qname,
            type=Type(question.qtype.value),
            class_=Class(question.qclass.value),
            ttl=record.ttl,
            rdata=rdata,
        )
        answers.append(rr)
    elif question.qtype == QType.CNAME and hasattr(record, "cname"):
        rdata = RDataCNAME(cname=record.cname)
        rr = DNSResourceRecord(
            name=question.qname,
            type=Type(question.qtype.value),
            class_=Class(question.qclass.value),
            ttl=record.ttl,
            rdata=rdata,
        )
        answers.append(rr)
    elif question.qtype == QType.NS and hasattr(record, "nsdname"):
        rdata = RDataNS(nsdname=record.nsdname)
        rr = DNSResourceRecord(
            name=question.qname,
            type=Type(question.qtype.value),
            class_=Class(question.qclass.value),
            ttl=record.ttl,
            rdata=rdata,
        )
        answers.append(rr)

        additional_q = DNSQuestion(
            qname=record.nsdname, qtype=QType.A, qclass=QClass.IN
        )
        additional_record = catalog.try_lookup_record(additional_q)
        if additional_record is None or not hasattr(additional_record, "host_address"):
            logger.warning(f'msg="No A record found for NS target {record.nsdname}"')
            return None
        rdata = RDataA(address=IPv4Address(additional_record.host_address))
        rr = DNSResourceRecord(
            name=question.qname,
            type=Type.A,
            class_=Class.IN,
            ttl=record.ttl,
            rdata=rdata,
        )
        additional.append(rr)
    else:
        return None

    query.header.flags.aa = 1
    query.set_answers(answers)
    query.set_additional(additional)

    return query
