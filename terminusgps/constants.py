import enum


class CommandFlag(enum.IntFlag):
    USE_ANY = 0
    USE_PRIMARY = 0x1
    USE_SECONDARY = 0x2
    SEND_PARAM = 0x10


class CommandLinkType(enum.StrEnum):
    AUTO = ""
    TCP = "tcp"
    UDP = "udp"
    VRT = "vrt"
    GSM = "gsm"
