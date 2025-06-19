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
    if not rr.requires_glue_record():
        return None

    domain_name = rr.rdata.domain_name_target
    if not domain_name:
        return None

    glue_question = DNSQuestion(
        qname=domain_name,
        qtype=QType.A,
        qclass=QClass.IN,
    )

    resolved = catalog.try_lookup_record(glue_question)
    if not resolved:
        logger.warning(f'msg="No record found for {glue_question.qname}"')
        return None

    record, origin = resolved
    return DNSResourceRecord.from_record(record, origin)


def try_resolve_query(catalog: Catalog, query: DNSMessage) -> bool:
    question = query.questions[0]

    resolved = catalog.try_lookup_record(question)
    if not resolved:
        return False

    record, origin = resolved

    answers: List[DNSResourceRecord] = []
    additional: List[DNSResourceRecord] = []

    rr = DNSResourceRecord.from_record(record, origin)
    answers.append(rr)

    glue_rr = try_glue_resource_record(catalog, rr)
    if glue_rr:
        additional.append(glue_rr)

    query.promote_to_response(recursion_supported=True)
    query.header.flags.aa = 1  # Authoritative Answer
    query.set_answers(answers)
    query.set_additional(additional)

    return True
