from passlib.hash import bcrypt
from getpass import getpass

import re


class Client:
    hasher = bcrypt.using(rounds=13)

    def __init__(self, password: str) -> None:
        self.password = password

    def main_menu_handler(self):
        Client.show_main_menu()
        while (command := input()) != "exit":
            if command == "1": self.connect_to_ext_servers()
            if command == "2": self.login_as_admin()
            else: self.invalid_command()

    def firewall_menu_handler(self):
        pass

    def messenger(self, proxy_port: int):
        pass

    def stream(self, proxy_port: int):
        pass

    def show_main_menu():
        for i, item in enumerate(CommandHandler.menu_times):
            print(f"{i + 1}. {CommandHandler.menu_times[item]}")

    def login_as_admin(self):
        while not Client.hasher.verify(getpass(), self.password):
            print("Wrong Password")
        self.firewall_menu_handler()

    def connect_to_ext_servers(self):
        while True:
            user_input = input()
            match = re.match("(?P<server>(Shalgham|Choghondar))( via (?P<port>\d+))?", user_input)
            if not match:
                print("Invalid Server name")
                continue
            server, port = match.groupdict()["server"], int(match.groupdict().get("port", 0))
            if server == "Shalgham": self.messenger(port)
            elif server == "Choghondar": self.stream(port)

    def invalid_command(self):
        print(CommandHandler.INVALID_COMMAND)


class CommandHandler:
    CONNECT_TO_EXT_SERVER = "connect"
    LOGIN_AS_ADMIN = "login"
    INVALID_COMMAND = 'Invalid Command'

    regexes = {
        CONNECT_TO_EXT_SERVER: re.compile("connect"),
        LOGIN_AS_ADMIN: re.compile("login")
    }

    menu_times = {
        CONNECT_TO_EXT_SERVER: "Connect to external servers",
        LOGIN_AS_ADMIN: "Login as admin"
    }

    handlers = {
        CONNECT_TO_EXT_SERVER: Client.messenger,
        LOGIN_AS_ADMIN: Client.login_as_admin,
        INVALID_COMMAND: Client.invalid_command
    }

    def parse(command):
        for pattern in CommandHandler.regexes.values():
            if (match := pattern.match(command)):
                return CommandHandler.handlers[match.group()]
        return CommandHandler.handlers[CommandHandler.INVALID_COMMAND]


if __name__ == "__main__":
    password = getpass("Set an admin password: ")

    client = Client(
        Client.hasher.hash(password)
    )
    # client.main_menu_handler()
    client.connect_to_ext_servers()
    