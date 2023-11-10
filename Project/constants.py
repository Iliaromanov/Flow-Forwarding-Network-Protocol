from enum import Enum, auto

LOCAL_IP         = "0.0.0.0"
FWD_REQUEST_PORT = 8000 # listen for broadcasts on this
REPLY_PORT       = 4000 # listen for replies to broadcasts on this


class PacketType(Enum):
    ANNOUCE_ENDPOINT    = 0  # used for packet sent by new client to edge router on init
    FWD_REQUEST         = 1  # can be used for both broadcast and known next hop packets
    FWD_REPLY           = 2  # used as reply to broadcasted forward requests


class PacketData(Enum):
    PACKET_TYPE = "packet_type"
    DEST_ADDR   = "dest_addr"
    HOP_COUNT   = "hop_count"
    BODY        = "body"