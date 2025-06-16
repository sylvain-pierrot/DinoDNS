from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dinodns.catalog import Record
from dinodns.core.rr.types import Type


class RData(ABC):
    @property
    def domain_name_target(self) -> Optional[str]:
        return None

    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes) -> "RData":
        raise NotImplementedError()

    @abstractmethod
    def to_bytes(self) -> bytes:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def rr_type(cls) -> Type:
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_record(cls, record: Record) -> "RData":
        raise NotImplementedError()

    @classmethod
    def requires_glue_record(cls) -> bool:
        return False


_registry: dict[Type, type[RData]] = {}


def register_rdata(cls: type[RData]):
    _registry[cls.rr_type()] = cls
    return cls


class RDataFactory:
    @staticmethod
    def from_bytes(qtype: Type, data: bytes) -> RData:
        return _registry[qtype].from_bytes(data)

    @staticmethod
    def from_record(record: Record) -> RData:
        type = Type[record.type]
        cls = _registry.get(type)
        if not cls:
            raise NotImplementedError(f"Unsupported RData type: {type}")
        return cls.from_record(record)

    @staticmethod
    def get_all_types() -> List[Type]:
        return list(_registry.keys())

    @staticmethod
    def get_all_classes() -> Dict[Type, type["RData"]]:
        return {rtype: rdata_cls for rtype, rdata_cls in _registry.items()}
