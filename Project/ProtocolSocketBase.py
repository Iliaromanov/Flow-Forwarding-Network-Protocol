from typing import Dict, Any, Tuple

import socket
from abc import ABC, abstractmethod
import threading
import struct

import util

class FlowForwardingProtocolSocketBase(ABC):
    def __init__(self, listen_timeout: int = util.LISTEN_TIMEOUT) -> None:
        # socket for sending broadcasts, next hop fwd packets, and replies
        self._send_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )

        # socket for listening to incoming broadcasts, next hop fwd packets, and replies
        self._listen_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )
        self._listen_socket.bind((util.LOCAL_IP, util.FWD_REQUEST_PORT))
        self._listen_socket.settimeout(listen_timeout)

    def send(
        self, header_data: Dict[util.PacketData], 
        target_ip: str, target_port: int, payload: bytearray = bytearray()
    ) -> None:
        header = self._create_header(
            header_data.get(util.PacketData.PACKET_TYPE),
            header_data.get(util.PacketData.DEST_ADDR),
            header_data.get(util.PacketData.HOP_COUNT, 0)
        )

        data = header + payload

        assert(len(data) < util.BUFFER_SIZE)

        self._send_socket.sendto(data, (target_ip, target_port))

    def broadcast(
        self, header_data: Dict[util.PacketData], payload: bytearray = bytearray()
    ) -> None:
        self.send(
            header_data, payload, 
            util.BROADCAST_IP, util.FWD_REQUEST_PORT
        )

    def receive(
        self, receive_on_send_socket: bool = False
    ) -> Tuple[Dict[util.PacketData, Any], Tuple[str, int]]:
        msg, addr = None, None
        if receive_on_send_socket:
            msg, addr = self._send_socket.recvfrom(util.BUFFER_SIZE)
        else:
            msg, addr = self._listen_socket.recvfrom(util.BUFFER_SIZE)

        return (self._parse_packet(msg), addr)


    def _listen(self) -> None:
        while self.listening:
            try:
                msg, addr = self._listen_socket.recvfrom(util.BUFFER_SIZE)
            except socket.timeout:
                
                # timeout to check if thread was asked to stop
                continue
            self.handle_received_message(
                self._parse_packet(msg), addr
            )
           

    def start_listen_thread(self) -> None:
        self.listening = True
        self._listen_thread = threading.Thread(
            target=self._listen
        )
        self._listen_thread.start()

    def stop_listen_thread(self) -> None:
        self.listening = False
        self._listen_thread.join()
    
    @abstractmethod
    def handle_received_message(
        self, parsed_packet: Dict[str, Any], sender_addr: Tuple[str, int]
    ) -> None:
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
            self, packet_type: util.PacketType, dest: str, hop_count: int) -> bytearray:
        header = bytearray()
        
        # packet type
        header.extend(struct.pack('B', packet_type.value))
        # destination
        header.extend(self._addr_to_bytes(dest))
        # hop count
        assert(hop_count < 255) # hop_count should fit in 1 byte, otherwise error out
        header.extend(struct.pack('B', hop_count))

        return header
    
    def _parse_packet(self, payload: bytes) -> Dict[util.PacketData, Any]:
        # ASSUMING BODY WILL BE AN ENCODED STR (so only sending text)
        return {
            util.PacketData.PACKET_TYPE: payload[0],
            util.PacketData.DEST_ADDR: self._hex_bytes_to_addr(
                payload[1:5]
            ),
            util.PacketData.HOP_COUNT: payload[5],
            util.PacketData.BODY: payload[6:].decode()
        }
    