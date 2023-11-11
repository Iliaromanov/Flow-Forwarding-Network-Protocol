from typing import Any, Dict, Tuple
from ProtocolSocketBase import FlowForwardingProtocolSocketBase
import util
from time import sleep


class Client(FlowForwardingProtocolSocketBase):
    def __init__(self, addr: str) -> None:
        super().__init__()
        self.addr = addr.replace(":", "").lower()
        assert(len(addr) == 11) # must be of format AA:AA:AA:AA
        assert(len(self.addr) == 8) # must be of format AAAAAAAA

        self._edge_router_ip = None
        self._attach_to_edge_router()

    def _attach_to_edge_router(self) -> None:
        # returns addr of edge router
        header = {
            util.PacketDataKey.PACKET_TYPE: util.PacketType.ANNOUNCE_ENDPOINT,
            util.PacketDataKey.DEST_ADDR: self.addr
        }
        # broadcast since the edge router should be the only container
        #  in the same network as this client
        
        sleep(1) # sleep 1 sec to allow router to start listening
        self.broadcast(header)

        # listen for ACK
        receive_ok, receive_data, receive_addr = self.receive(
            receive_on_send_socket=True
        )
        if receive_ok:
            assert(
                receive_data[util.PacketDataKey.PACKET_TYPE] == \
                util.PacketType.ANNOUNCE_ENDPOINT_ACK.value
            )
            self._edge_router_ip = receive_addr[0]
        else:
            util.Logger.error("Failed to announce self to edge router")
            self.close_sockets()
            exit()

    def handle_received_message(
        self, parsed_packet: Dict[util.PacketDataKey, Any], sender_addr: Tuple[str, int]
    ) -> None:
        packet_type = parsed_packet[util.PacketDataKey.PACKET_TYPE]

        match packet_type:
            case util.PacketType.FWD_REQUEST.value:
                # could be direct msg from router
                #  or accidental broadcast (ignore latter)
                pass
            case util.PacketType.FWD_REPLY.value:
                # could be 
                pass
            case _:
                util.Logger.error(
                    f"Client received invalid message type: {packet_type}"
                )

        return None

    
