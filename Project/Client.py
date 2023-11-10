from ProtocolSocketBase import FlowForwardingProtocolSocketBase


class Client(FlowForwardingProtocolSocketBase):
    def __init__(self, addr: str) -> None:
        self.addr = addr.replace(":", "").lower()
        assert(len(self.addr) == 8) # must be of format AA:AA:AA:AA