# Flow-Forwarding-Network-Protocol

A protocol I built on top of UDP for forwarding flows of packets using concepts from Direct Vector Routing to determine routes between senders and destinations. One of the key goals of this protocol was to enable network nodes to send/receive packets to on another without knowing exact IP addresses of any other node in the network, intead each node would build local forwarding tables to make routing decisions and forward flows toward requested destination nodes.

## Running a demo topology

I used docker compose to configure and run a network of nodes (each node as an isolated docker container running my protocol code) consisting of two types of actors: Sender nodes and Route nodes. The systems allows senders to communicate between each other by broadcasting messages to the networks of routers in between them.
