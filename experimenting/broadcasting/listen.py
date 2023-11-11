import socket

print("listener up")

udp_socket = socket.socket(
    socket.AF_INET, socket.SOCK_DGRAM
)

udp_socket.bind(("0.0.0.0", 12345))

data, addr = udp_socket.recvfrom(2048)

print(f"Received data {data.decode()} from {addr}")
