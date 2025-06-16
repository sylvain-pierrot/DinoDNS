from typing import List, Optional
from dinodns.catalog import Catalog
from dinodns.core.message import DNSMessage
from dinodns.core.question import DNSQuestion, QClass, QType
from dinodns.core.rr.resource_record import (
    DNSResourceRecord,
)
import logging


logger = logging.getLogger(__name__)


def try_glue_resource_record(
    catalog: Catalog, rr: DNSResourceRecord
) -> "Optional[DNSResourceRecord]":
    if not rr.is_rdata_domain_name():
        return None

    domain_name = rr.rdata.target_name
    if not domain_name:
        return None

    glue_question = DNSQuestion(
        qname=domain_name,
        qtype=QType.A,
        qclass=QClass.IN,
    )
    record = catalog.try_lookup_record(glue_question)
    if record is None:
        logger.warning(f'msg="No record found for {glue_question.qname}"')
        return None

    return DNSResourceRecord.from_record(record)


def try_resolve_query(catalog: Catalog, query: DNSMessage) -> None:
    question = query.questions[0]

    if question.qclass != QClass.IN:
        return None

    record = catalog.try_lookup_record(question)
    if record is None:
        logger.warning(f'msg="No record found for {question.qname}"')
        return None

    answers: List[DNSResourceRecord] = []
    additional: List[DNSResourceRecord] = []

    rr = DNSResourceRecord.from_record(record)
    answers.append(rr)

    glue_rr = try_glue_resource_record(catalog, rr)
    if glue_rr:
        additional.append(glue_rr)

    query.header.flags.aa = 1
    query.set_answers(answers)
    query.set_additional(additional)
