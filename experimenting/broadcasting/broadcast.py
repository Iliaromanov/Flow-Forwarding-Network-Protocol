import socket

# Set up a UDP socket
udp_socket = socket.socket(
    socket.AF_INET, socket.SOCK_DGRAM
)

# Enable broadcasting on the socket
udp_socket.setsockopt(
    socket.SOL_SOCKET, socket.SO_BROADCAST, 1
)

# Define the broadcast address and port
broadcast_address = "255.255.255.255"  # This is the broadcast address for most networks
broadcast_port = 12345  # Choose whatever port number

# Your message to broadcast
message = "Hello, this is a broadcast message!"

# Send the broadcast message
udp_socket.sendto(
    message.encode(), 
    (broadcast_address, broadcast_port)
)
print(f"Broadcasted message: '{message}'")
