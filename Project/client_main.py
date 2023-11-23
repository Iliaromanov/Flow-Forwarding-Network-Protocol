import sys

import util
from Client import Client

def main():
    assert(len(sys.argv) == 2)
    addr = sys.argv[1]
    client = Client(addr)
    print("Client endpoint initialized and listening ...")
    print("cmd:")
    print(
        f"- {util.Commands.SEND.value} [dest] Optional[path_to_data] - " + \
        "send data located at 'path_to_data' to endpoint with ID 'dest'"
    )
    print(f"- {util.Commands.EXIT.value} - end program")

    while True:
        print("-" * 10)
        cmd = input(f"Client - {addr} - waiting on input ...\n> ").split()

        match cmd[0]:
            case util.Commands.SEND.value:
                dest = cmd[1]
                path_to_data = ""
                if len(cmd) > 2:
                    path_to_data = cmd[2]
                client.send_to(dest, path_to_data)
            case util.Commands.EXIT.value:
                client.clean_exit()
                exit()
            case _:
                util.Logger.error("Invalid command")

if __name__ == "__main__":
    main()