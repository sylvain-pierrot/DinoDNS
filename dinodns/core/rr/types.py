from enum import Enum


class Type(Enum):
    UNKNOWN = -1
    A = 1
    NS = 2
    MD = 3
    MF = 4
    CNAME = 5
    SOA = 6
    MB = 7
    MG = 8
    MR = 9
    NULL = 10
    WKS = 11
    PTR = 12
    HINFO = 13
    MINFO = 14
    MX = 15
    TXT = 16
    AAAA = 28
    SRV = 33

    @classmethod
    def _missing_(cls, value: object):
        obj = object.__new__(cls)
        obj._name_ = "UNKNOWN"
        obj._value_ = value
        return obj
