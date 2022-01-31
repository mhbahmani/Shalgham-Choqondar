from passlib.hash import bcrypt
from getpass import getpass

import re


class Client:
    hasher = bcrypt.using(rounds=13)

    def __init__(self, password: str) -> None:
        self.password = password

    def main_menu_handler(self):
        while True:
            Client.show_main_menu()
            command = input()
            handler = CommandHandler.parse(command)
            handler()

    def messenger():
        pass

    def stream(self):
        pass

    def firewall(self):
        pass

    def show_main_menu():
        for i, item in enumerate(CommandHandler.menu_times):
            print(f"{i + 1}. {CommandHandler.menu_times[item]}")

    def login_as_admin():
        pass

    def invalid_command():
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
    client.main_menu_handler()
    