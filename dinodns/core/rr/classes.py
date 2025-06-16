from enum import Enum


class Class(Enum):
    UNKNOWN = -1
    IN = 1  # Internet class
    CS = 2  # CSNET class (obsolete)
    CH = 3  # CHAOS class (obsolete)
    HS = 4  # Hesiod class (obsolete)

    @classmethod
    def _missing_(cls, value: object):
        obj = object.__new__(cls)
        obj._name_ = "UNKNOWN"
        obj._value_ = value
        return obj
