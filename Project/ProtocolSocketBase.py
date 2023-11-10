from typing import Dict, Any

import socket
from abc import ABC, abstractmethod
from threading import Thread
import struct

import constants as const

class FlowForwardingProtocolSocketBase(ABC):
    def __init__(self) -> None:
        # socket for sending broadcasts, next hop fwd packets, and replies
        self.send_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )

        # socket for listening to incoming broadcasts, next hop fwd packets, and replies
        self.listen_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )
        self.fwd_listen_socket.bind((const.LOCAL_IP, const.FWD_REQUEST_PORT))

    def _send(
            self, header_data: Dict[const.PacketData], 
            dest_ip: str, dest_port: int, payload: bytearray = bytearray()
        ) -> None:
        pass

    def _listen(self) -> None:
        pass

    def _start_listening(self) -> None:
        pass

    def _stop_listening(self) -> None:
        pass
    
    @abstractmethod
    def handle_received_message(self, reply_data: Dict[str, Any]) -> None:
        pass
        
        # would be called in _listen with the parsed packet data (reply_data)
        # then have a switch / if statement to detrmine what packet type it is
        #  and what to do based on where this abstract method is implemented

    def _addr_to_bytes(hex_address: str) -> bytes:
        # converts an endpoints address to bytes
        assert(len(hex_address) == 8) # must be of format aabbccdd
        return bytes.fromhex(hex_address)

    def _hex_bytes_to_addr(hex_bytes: bytes) -> str:
        # converts the bytes of an addr to corresponding string
        assert(len(hex_bytes) == 4) # must be 4-byte addr
        return hex_bytes.hex()

    def _create_header(
            self, packet_type: const.PacketType, dest: str, hop_count: int) -> bytearray:
        header = bytearray()
        
        # packet type
        header.extend(struct.pack('B', packet_type.value))
        # destination
        header.extend(self._addr_to_bytes(dest))
        # hop count
        header.extend(struct.pack('B', hop_count))

        return header
    
    def _parse_packet(self, payload: bytes) -> Dict[const.PacketData, Any]:
        # ASSUMING BODY WILL BE AN ENCODED STR (so only sending text)
        return {
            const.PacketData.PACKET_TYPE: payload[0],
            const.PacketData.DEST_ADDR: self._hex_bytes_to_addr(
                payload[1:5]
            ),
            const.PacketData.HOP_COUNT: payload[5],
            const.PacketData.BODY: payload[6:].decode()
        }
    