from typing import Any, Dict, Tuple, List

from ProtocolSocketBase import FlowForwardingProtocolSocketBase
import util

class Router(FlowForwardingProtocolSocketBase):
    def __init__(self) -> None:
        super().__init__()
        self._endpoint_id = None
        self._endpoint_ip = None
        self._fwd_table: Dict[str, Dict[util.FwdTableKey, Any]] = {}

    def _attach_endpoint(self, addr: str, endpoint_ip: str) -> None:
        self._endpoint_id = addr
        self._endpoint_ip = endpoint_ip

        # reply with ACK
        header = {
            util.PacketDataKey.PACKET_TYPE: util.PacketType.ANNOUNCE_ENDPOINT_ACK
        }
        self.send(header, endpoint_ip, util.SEND_PORT)

        util.Logger.info(f"Attached endpoint {addr}")

    def _handle_fwd_request(self, dest: str, body: str, requesters_ip: str) -> None:
        # check if self._endpoint == dest
        # otherwise check fwd table (read note point at top of Implement Plan)
        util.Logger.info(f"received fwd request to {dest}", sock="listen")
        
        header = {
            util.PacketDataKey.PACKET_TYPE: util.PacketType.FWD_REQUEST,
            util.PacketDataKey.DEST_ADDR: dest
        }

        if self._endpoint_id is not None and self._endpoint_id == dest:
            util.Logger.info(
                f"Received fwd request to this Router's endpoint; " + \
                "directly forwarding to endpoint",
                sock="listen"
            )
            if dest not in self._fwd_table:
                self._fwd_table[dest] = {
                    util.FwdTableKey.NEXT_HOP: None,
                    util.FwdTableKey.HOP_COUNT: None,
                }
            if util.FwdTableKey.REQUESTERS in self._fwd_table[dest]:
                self._fwd_table[dest][
                    util.FwdTableKey.REQUESTERS
                ].add(requesters_ip)
            else:
                self._fwd_table[dest][util.FwdTableKey.REQUESTERS] = set(
                    [requesters_ip]
                )
            util.Logger.info(
                f"requesters: {self._fwd_table[dest][util.FwdTableKey.REQUESTERS]}",
                sock="listen"
            )
            self.send(
                header_data=header,
                target_ip=self._endpoint_ip,
                target_port=util.LISTEN_PORT,
                payload=body.encode()
            )
        else:
            if dest not in self._fwd_table:
                # first time seeing this, need to broadcast to find path
                util.Logger.info(f"{dest} not in fwd table", sock="listen")
                self._fwd_table[dest] = {
                    util.FwdTableKey.NEXT_HOP: None,
                    util.FwdTableKey.HOP_COUNT: None,
                    util.FwdTableKey.REQUESTERS: set([requesters_ip])
                }

                util.Logger.info(
                    f"requesters: {self._fwd_table[dest][util.FwdTableKey.REQUESTERS]}",
                    sock="listen"
                )

                self.broadcast(header_data=header, payload=body.encode())
            elif self._fwd_table[dest][util.FwdTableKey.NEXT_HOP] is None:
                # this means already broadcasted for this dest
                #  so to avoid circular broadcast, ignore
                util.Logger.info(
                    f"{dest} already in fwd table but unknown next hop;" + \
                    " only adding to requesters array, but not broadcasting again",
                    sock="listen"
                )
                self._fwd_table[dest][
                    util.FwdTableKey.REQUESTERS
                ].add(requesters_ip)

                util.Logger.info(
                    f"requesters: {self._fwd_table[dest][util.FwdTableKey.REQUESTERS]}",
                    sock="listen"
                )

            else:
                # the path to dest is known through next hop in fwd table
                util.Logger.info(
                    f"Next Hop to {dest} is know through fwd table;" + \
                    "sending directly",
                    sock="listen"
                )
                self.send(
                    header_data=header,
                    target_ip=self._fwd_table[dest][util.FwdTableKey.NEXT_HOP],
                    target_port=util.LISTEN_PORT,
                    payload=body.encode()
                )

    def _handle_fwd_reply(
        self, dest: str, hop_count: int, reply_body: str, reply_ip: str
    ) -> None:
        util.Logger.info(f"received reply for dest: {dest}", sock="listen")
        # if received reply, the dest must be in fwd table
        assert(dest in self._fwd_table)
        assert(hop_count > 0) # zero means no hop count was sent

        if self._fwd_table[dest][util.FwdTableKey.NEXT_HOP] is None or \
           self._fwd_table[dest][util.FwdTableKey.HOP_COUNT] >= hop_count:
            # equal because we want known path replies to go through
            util.Logger.info(
                "updating forward table: " + \
                f"hop_count={hop_count}, next_hop={reply_ip}",
                sock="listen"          
            )
            # update next hop and hop count
            self._fwd_table[dest][util.FwdTableKey.HOP_COUNT] = hop_count
            self._fwd_table[dest][util.FwdTableKey.NEXT_HOP] = reply_ip

            util.Logger.info(
                f"replying to requesters: {self._fwd_table[dest][util.FwdTableKey.REQUESTERS]}",
                sock="listen"
            )

            # forward reply to all requesters 
            # NO NEED TO remove requesters after reply becuase
            #  even if there is a circular requestor, the hop count goes up each time 
            #    so the reply chain would terminate
            # but not removing ensures minimum number of hops is always used.

            # REQUESTERS includes endpoint that sent the inital request
            for requester in self._fwd_table[dest][util.FwdTableKey.REQUESTERS]:
                header = {
                    util.PacketDataKey.PACKET_TYPE: util.PacketType.FWD_REPLY,
                    util.PacketDataKey.DEST_ADDR: dest,
                    util.PacketDataKey.HOP_COUNT: hop_count + 1,
                }
                response_body = f"{reply_body},{requester}"
                self.send(
                    header_data=header,
                    target_ip=requester,
                    target_port=util.LISTEN_PORT,
                    payload=response_body.encode()
                )
        else:
            util.Logger.info(
                f"A next_hop to {dest} with lesser hop_count " + \
                f"({self._fwd_table[dest][util.FwdTableKey.HOP_COUNT]} < {hop_count})" + \
                " exists in fwd table; ignoring this reply",
                sock="listen"    
            )

    
    # all of this runs in the listen thread
    def handle_received_message(
        self, parsed_packet: Dict[util.PacketDataKey, Any], 
        sender_addr: Tuple[str, int]
    ) -> None:
        packet_type = parsed_packet[util.PacketDataKey.PACKET_TYPE]
        
        match packet_type:
            case util.PacketType.ANNOUNCE_ENDPOINT.value:
                util.Logger.info(
                    f"Received announce endpoint packet from {sender_addr[0]}",
                    sock="listen"
                )

                self._attach_endpoint(
                    parsed_packet[util.PacketDataKey.DEST_ADDR],
                    sender_addr[0]
                )
            case util.PacketType.FWD_REQUEST.value:
                # for broadcast and when this router 
                #   is next_hop in the senders fwd_table
                util.Logger.info(
                    f"Received fwd request packet from {sender_addr[0]}",
                    sock="listen"
                )
                self._handle_fwd_request(
                    parsed_packet[util.PacketDataKey.DEST_ADDR],
                    parsed_packet[util.PacketDataKey.BODY],
                    sender_addr[0]
                )
            case util.PacketType.FWD_REPLY.value:
                # for when someone this router requested data from
                #   replies
                util.Logger.info(
                    f"Received fwd reply packet from {sender_addr[0]}",
                    sock="listen"
                )

                self._handle_fwd_reply(
                    parsed_packet[util.PacketDataKey.DEST_ADDR],
                    int(parsed_packet[util.PacketDataKey.HOP_COUNT]),
                    parsed_packet[util.PacketDataKey.BODY],
                    sender_addr[0]
                )
            case _:
                util.Logger.error(
                    f"Router received invalid message type: {packet_type}",
                    sock="listen"
                )
