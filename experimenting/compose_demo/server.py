import socket
import sys
import constants as const


def main(argv):
    localIP     = "0.0.0.0"
    bufferSize  = 65535
    reply = "Hello UDP Client".encode()

    # Create a datagram socket
    comms = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Bind to address and ip
    comms.bind((localIP, const.SERVER_PORT))

    print("Server up and listening", flush=True)

    # Listen for incoming datagrams
    while(True):
        message, addr = comms.recvfrom(bufferSize)
        print("From:", addr, ":", message, flush=True)

        # Sending a reply to client
        comms.sendto(reply, addr)

if __name__ == "__main__":
    main(sys.argv[1:])