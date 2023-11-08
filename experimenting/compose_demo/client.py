import sys
import socket
import constants as const


def main(argv):
    data       = "Hello UDP Server".encode()
    bufferSize = 65535

    # Use the first argument as name of the server to contact
    # omitted all checks and safety here
    addr = (argv[0], const.SERVER_PORT)

    # Create a UDP socket at client side
    comms = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    # Send to server using created UDP socket
    comms.sendto(data, addr)

    data, addr = comms.recvfrom(bufferSize)
    print("From:", addr, ":", data)

if __name__ == "__main__":
    main(sys.argv[1:])