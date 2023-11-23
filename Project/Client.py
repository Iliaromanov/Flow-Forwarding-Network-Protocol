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
        self._awaiting_response_from = set()
        self._attach_to_edge_router()

    def send_to(self, dest: str, path_to_data: str = "") -> None:
        dest = dest.replace(":", "").lower()

        header = {
            util.PacketDataKey.PACKET_TYPE: util.PacketType.FWD_REQUEST,
            util.PacketDataKey.DEST_ADDR: dest
        }

        if path_to_data != "":
            # handle this later
            pass

        self.send(
            header_data=header, 
            target_ip=self._edge_router_ip, target_port=util.LISTEN_PORT
        )

        self._awaiting_response_from.add(dest)

    def clear_request(self) -> None:
        # requests to clear self from all fwd tables
        util.Logger.info("sending request to clear self address from fwd tables")
        header = {
            util.PacketDataKey.PACKET_TYPE: util.PacketType.CLEAR_REQUEST,
            util.PacketDataKey.DEST_ADDR: self.addr
        }
        self.send(
            header_data=header, 
            target_ip=self._edge_router_ip, target_port=util.LISTEN_PORT
        )

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

    def _handle_fwd_request(self, dest: str, body: str) -> None:
        if dest != self.addr:
            util.Logger.info("Request to fwd to self; ignoring", sock="listen")
            return
        
        # this client is the destination of a request from another client
        util.Logger.info(f"Request from other client has reached its destination!", sock="listen")
        util.Logger.info(f"Received request body: {body}", sock="listen")
        
        # reply to edge router
        header = {
            util.PacketDataKey.PACKET_TYPE: util.PacketType.FWD_REPLY,
            util.PacketDataKey.DEST_ADDR: self.addr,
            util.PacketDataKey.HOP_COUNT: 1
        }

        # reply will contain the path to this client in body once it arrives at
        #  sending client
        response_body = f"{self.addr},{self._edge_router_ip}"

        self.send(
            header_data=header, 
            target_ip=self._edge_router_ip,
            target_port=util.LISTEN_PORT,
            payload=response_body.encode() 
        )

    def _handle_reply(self, dest: str, body: str) -> None:
        if dest not in self._awaiting_response_from:
            # util.Logger.info(
            #     f"received reply for '{dest}', but have already"
            # )
            return
        
        self._awaiting_response_from.remove(dest)

        util.Logger.info(
            f"Received ACK reply for dest: {dest}", sock="listen"
        )
        path_to_dest = " -> ".join(body.split(",")[::-1])
        util.Logger.info(
            f"The path to dest={dest} (from response) is {path_to_dest}", 
            sock="listen"
        )


    def handle_received_message(
        self, parsed_packet: Dict[util.PacketDataKey, Any], sender_addr: Tuple[str, int]
    ) -> None:
        packet_type = parsed_packet[util.PacketDataKey.PACKET_TYPE]

        match packet_type:
            case util.PacketType.FWD_REQUEST.value:
                # could be direct msg from router
                #  or accidental broadcast (ignore latter)
                util.Logger.info(
                    f"Received fwd request packet from {sender_addr[0]}", sock="listen"
                )
                self._handle_fwd_request(
                    parsed_packet[util.PacketDataKey.DEST_ADDR],
                    parsed_packet[util.PacketDataKey.BODY]
                )
            case util.PacketType.FWD_REPLY.value:
                self._handle_reply(
                    parsed_packet[util.PacketDataKey.DEST_ADDR],
                    parsed_packet[util.PacketDataKey.BODY]
                )
            case util.PacketType.ANNOUNCE_ENDPOINT.value:
                # caused by broadcast to self; do nothing
                pass
            case _:
                util.Logger.error(
                    f"Client received invalid message type: {packet_type}",
                )

        return None

    
