from Router import Router
import util
import sys

def main():
    router = Router()
    print("Router initialized and listening ...")

    while True:
        print("-" * 10)
        cmd = input(f"Type '{util.Commands.EXIT.value}' to end router program \n").split()
        if cmd[0] == util.Commands.EXIT.value:
            router.clean_exit()
            exit()
        else:
            util.Logger.error("Invalid command.")


if __name__ == "__main__":
    main()
