from typing import Any, Dict, Tuple, Union

from ProtocolSocketBase import FlowForwardingProtocolSocketBase
import util

class Router(FlowForwardingProtocolSocketBase):
    def __init__(self) -> None:
        super().__init__()
        self._endpoint_id = None
        self._endpoint_ip = None
        self._fwd_table: Dict[str, Dict[util.FwdTableKey, Union[int, str]]] = {}

    def _attach_endpoint(self, addr: str, endpoint_ip: str) -> None:
        self._endpoint = addr
        self._endpoint_ip = endpoint_ip

        # reply with ACK
        header = {
            util.PacketDataKey.PACKET_TYPE: util.PacketType.ANNOUNCE_ENDPOINT_ACK
        }
        self.send(header, endpoint_ip, util.SEND_PORT)

        util.Logger.info(f"Attached endpoint {addr}")

    def _handle_fwd_request(self, dest: str, requester_ip: str) -> None:
        # check if self._endpoint == dest
        # otherwise check fwd table (read note point at top of Implement Plan)
        pass

    def _handle_fwd_reply(self, dest: str, hop_count: int, reply_ip: str) -> None:
        # set reply_ip as next hop to dest if
        #  self.fwd_table[util.FwdTableKey.HOP_COUNT] is None or \
        #  self.fwd_table[util.FwdTableKey.HOP_COUNT] > hop_count
        # then send the reply to self.fwd_table[util.FwdTableKey.REQUESTER]
        pass
    
    # all of this runs in the listen thread
    def handle_received_message(
        self, parsed_packet: Dict[util.PacketDataKey, Any], 
        sender_addr: Tuple[str, int]
    ) -> None:
        packet_type = parsed_packet[util.PacketDataKey.PACKET_TYPE]
        
        match packet_type:
            case util.PacketType.ANNOUNCE_ENDPOINT.value:
                util.Logger.info(
                    f"Received announce endpoint packet from {sender_addr[0]}"
                )

                self._attach_endpoint(
                    parsed_packet[util.PacketDataKey.DEST_ADDR],
                    sender_addr[0]
                )
            case util.PacketType.FWD_REQUEST.value:
                # for broadcast and when this router 
                #   is next_hop in the senders fwd_table
                util.Logger.info(
                    f"Received fwd request packet from {sender_addr[0]}"
                )
                self._handle_fwd_request(
                    parsed_packet[util.PacketDataKey.DEST_ADDR],
                    sender_addr[0]
                )
            case util.PacketType.FWD_REPLY.value:
                # for when someone this router requested data from
                #   replies
                util.Logger.info(
                    f"Received fwd reply packet from {sender_addr[0]}"
                )

                self._handle_fwd_reply(
                    parsed_packet[util.PacketDataKey.DEST_ADDR],
                    int(parsed_packet[util.PacketDataKey.HOP_COUNT]),
                    sender_addr[0]
                )
            case _:
                util.Logger.error(
                    f"Router received invalid message type: {packet_type}"
                )
