from typing import List, Optional
from dinodns.catalog import Catalog, NSRecord
from dinodns.core.message import DNSMessage
from dinodns.core.question import DNSQuestion, QClass, QType
from dinodns.core.rr.rdata.base import RDataFactory
from dinodns.core.rr.resource_record import (
    Class,
    DNSResourceRecord,
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

    rdata = RDataFactory.from_record(record)
    rr = DNSResourceRecord(
        name=question.qname,
        type=Type(question.qtype.value),
        class_=Class(question.qclass.value),
        ttl=record.ttl,
        rdata=rdata,
    )
    answers.append(rr)

    if isinstance(record, NSRecord):
        glue_name = record.nsdname
        glue_question = DNSQuestion(
            qname=record.nsdname, qtype=QType.A, qclass=QClass.IN
        )
        glue_record = catalog.try_lookup_record(glue_question)

        if glue_record and hasattr(glue_record, "host_address"):
            glue_rdata = RDataFactory.from_record(glue_record)
            glue_rr = DNSResourceRecord(
                name=glue_name,
                type=Type.A,
                class_=Class.IN,
                ttl=glue_record.ttl,
                rdata=glue_rdata,
            )
            additional.append(glue_rr)
        else:
            logger.warning(f'msg="No glue A record found for NS target {glue_name}"')

    query.header.flags.aa = 1
    query.set_answers(answers)
    query.set_additional(additional)

    return query
