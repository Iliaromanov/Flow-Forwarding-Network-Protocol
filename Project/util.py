from enum import Enum, auto

LOCAL_IP         = "0.0.0.0"
LOOP_BACK_IP     = "127.0.0.1" # IP addr for sending packet to self
BROADCAST_IP     = "255.255.255.255"
FWD_REQUEST_PORT = 8000 # listen for broadcasts on this
REPLY_PORT       = 4000 # listen for replies to broadcasts on this
BUFFER_SIZE      = 1024
LISTEN_TIMEOUT   = 5    # every 5 seconds a listen would check if a request to kill thread was sent


class PacketType(Enum):
    ANNOUCE_ENDPOINT    = 0  # used for packet sent by new client to edge router on init
    FWD_REQUEST         = 1  # can be used for both broadcast and known next hop packets
    FWD_REPLY           = 2  # used as reply to broadcasted forward requests


class PacketData(Enum):
    PACKET_TYPE = "packet_type"
    DEST_ADDR   = "dest_addr"
    HOP_COUNT   = "hop_count"
    BODY        = "body"


class Logger:
    @staticmethod
    def info(msg: str) -> None:
        print(f"- INFO: {msg}")
    
    @staticmethod
    def critical(msg: str) -> None:
        print(f"\n--- !!! {msg} !!! ---\n")

    @staticmethod
    def warning(msg: str) -> None:
        print(f"- WARNING: {msg}")

    @staticmethod
    def error(msg: str) -> None:
        print(f"\n- ERROR: {msg}\n")
