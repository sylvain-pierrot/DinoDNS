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

    def byte_length(self) -> int:
        return len(self.to_bytes())


_registry: dict[Type, type[RData]] = {}


def register_rdata(cls: type[RData]):
    _registry[cls.rr_type()] = cls
    return cls


class RDataFactory:
    @staticmethod
    def from_bytes(type: Type, data: bytes) -> RData:
        rdata_type = _registry.get(type)
        if rdata_type is None:
            raise NotImplementedError(f"Unsupported Type: {type.name} ({type.value})")
        return rdata_type.from_bytes(data)

    @staticmethod
    def from_record(record: Record) -> RData:
        type = Type[record.type]
        cls = _registry.get(type)
        if not cls:
            raise NotImplementedError(f"Unsupported Type: {type}")
        return cls.from_record(record)

    @staticmethod
    def get_all_types() -> List[Type]:
        return list(_registry.keys())

    @staticmethod
    def get_all_classes() -> Dict[Type, type["RData"]]:
        return {rtype: rdata_cls for rtype, rdata_cls in _registry.items()}
