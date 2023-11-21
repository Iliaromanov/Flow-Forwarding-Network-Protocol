import socket
from time import sleep

# Set up a UDP socket
udp_socket = socket.socket(
    socket.AF_INET, socket.SOCK_DGRAM
)

# Enable broadcasting on the socket
udp_socket.setsockopt(
    socket.SOL_SOCKET, socket.SO_BROADCAST, 1
)

# Define the broadcast address and port
broadcast_address = "<broadcast>"  # This is the broadcast address for most networks
broadcast_port = 12345  # Choose whatever port number

# Your message to broadcast
message = "Hello, this is a broadcast message!"

sleep(2)
# Send the broadcast message
udp_socket.sendto(
    message.encode(), 
    (broadcast_address, broadcast_port)
)
print(f"Broadcasted message: '{message}'")
udp_socket.sendto(
    message.encode(), 
    (broadcast_address, broadcast_port)
)
print(f"AGAIN   Broadcasted message: '{message}'")

message_direct = "this is direct message!"

udp_socket.sendto(message_direct.encode(), ("router3", broadcast_port))

print(f"sent direct message {message_direct}")
