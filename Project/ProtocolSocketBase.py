from typing import Dict, Any, Tuple, Union

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
        self._send_socket.bind((util.LOCAL_IP, util.SEND_PORT))
        self._send_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_BROADCAST, 1
        )

        # socket for listening to incoming broadcasts, next hop fwd packets, and replies
        self._listen_socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )
        self._listen_socket.bind((util.LOCAL_IP, util.LISTEN_PORT))

        # set timeout for receives
        # self._listen_socket.settimeout(listen_timeout)

        self.start_listen_thread()

    def send(
        self, header_data: Dict[util.PacketDataKey, Any], 
        target_ip: str, target_port: int, payload: bytearray = bytearray()
    ) -> None:
        util.Logger.info(f"sending data to {target_ip}")
        header = self._create_header(
            header_data.get(util.PacketDataKey.PACKET_TYPE),
            header_data.get(util.PacketDataKey.DEST_ADDR, util.DEFAULT_DEST_ADDR),
            header_data.get(util.PacketDataKey.HOP_COUNT, 0)
        )

        data = header + payload

        assert(len(data) < util.BUFFER_SIZE)

        self._send_socket.sendto(data, (target_ip, target_port))

    def broadcast(
        self, header_data: Dict[util.PacketDataKey, Any], payload: bytearray = bytearray()
    ) -> None:
        self.send(
            header_data, 
            util.BROADCAST_IP, util.LISTEN_PORT,
            payload
        )

    def receive(
        self, receive_on_send_socket: bool = False, retry: int = 1
    ) -> Tuple[bool, Tuple[Dict[util.PacketDataKey, Any], Tuple[str, int]]]:
        msg, addr = None, None
        if receive_on_send_socket:
            try:
                msg, addr = self._send_socket.recvfrom(util.BUFFER_SIZE)
            except socket.timeout:
                retry -= 1
                if retry > 0:
                    util.Logger.warning(
                        "retrying send socket recieve after timeout"
                    )
                    return self.receive(receive_on_send_socket, retry)
                return (False, dict(), tuple())
        else:
            try:
                msg, addr = self._listen_socket.recvfrom(util.BUFFER_SIZE)
            except socket.timeout:
                retry -= 1
                if retry > 0:
                    util.Logger.warning(
                        "retrying listen socket recieve after timeout"
                    )
                    return self.receive(receive_on_send_socket, retry)
                return (False, dict(), tuple())

        return (True, self._parse_packet(msg), addr)


    def _listen(self) -> None:
        while self.listening:
            try:
                util.Logger.info("listen_socket listening ...")
                msg, addr = self._listen_socket.recvfrom(util.BUFFER_SIZE)
            except socket.timeout:
                util.Logger.warning(
                    "checking for thread stop; restarting receive after timeout"
                )
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
        self, parsed_packet: Dict[util.PacketDataKey, Any], sender_addr: Tuple[str, int]
    ) -> None:
        pass
        
        # would be called in _listen with the parsed packet data (reply_data)
        # then have a switch / if statement to detrmine what packet type it is
        #  and what to do based on where this abstract method is implemented

    @staticmethod
    def _addr_to_bytes(hex_address: str) -> bytes:
        # converts an endpoints address to bytes
        assert(len(hex_address) == 8) # must be of format aabbccdd
        return bytes.fromhex(hex_address)

    @staticmethod
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
    
    def _parse_packet(self, payload: bytes) -> Dict[util.PacketDataKey, Any]:
        # ASSUMING BODY WILL BE AN ENCODED STR (so only sending text)
        return {
            util.PacketDataKey.PACKET_TYPE: payload[0],
            util.PacketDataKey.DEST_ADDR: self._hex_bytes_to_addr(
                payload[1:5]
            ),
            util.PacketDataKey.HOP_COUNT: payload[5],
            util.PacketDataKey.BODY: payload[6:].decode()
        }
    
    def close_sockets(self) -> None:
        self._send_socket.close()
        self._listen_socket.close()
    
    def clean_exit(self) -> None:
        self.close_sockets()
        self.stop_listen_thread()
