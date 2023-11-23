from enum import Enum, auto

LOCAL_IP          = "0.0.0.0"
BROADCAST_IP      = "255.255.255.255"
DEFAULT_DEST_ADDR = "aaaaaaaa"
LISTEN_PORT       = 12345 # listen for broadcasts, replies on this
SEND_PORT         = 54321 # port for when send_socket needs to listen (eg use for ACKs)
BUFFER_SIZE       = 1024
LISTEN_TIMEOUT    = 5    # every 5 seconds a listen would check if a request to kill thread was sent


class PacketType(Enum):
    ANNOUNCE_ENDPOINT     = 0  # used for packet sent by new client to edge router on init
    ANNOUNCE_ENDPOINT_ACK = 1  # the edge router replies with this to let the client know router ip
    FWD_REQUEST           = 2  # can be used for both broadcast and known next hop packets
    FWD_REPLY             = 3  # used as reply to broadcasted forward requests


class PacketDataKey(Enum):
    PACKET_TYPE = "packet_type"
    DEST_ADDR   = "dest_addr"
    HOP_COUNT   = "hop_count"
    BODY        = "body"


class FwdTableKey(Enum):
    NEXT_HOP  = auto()
    HOP_COUNT = auto()
    REQUESTERS = auto()


class Commands(Enum):
    SEND = "send_to"
    EXIT = "exit"


class Logger:
    @staticmethod
    def info(msg: str, sock: str = "main") -> None:
        print(f"- [{sock}] INFO: {msg}")
    
    @staticmethod
    def critical(msg: str) -> None:
        print(f"\n--- !!! {msg} !!! ---\n")

    @staticmethod
    def warning(msg: str) -> None:
        print(f"- WARNING: {msg}")

    @staticmethod
    def error(msg: str) -> None:
        print(f"\n- ERROR: {msg}\n")
