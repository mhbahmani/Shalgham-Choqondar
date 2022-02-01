from meta import SingletonMeta

import re


class MainMenu(metaclass=SingletonMeta):
    CONNECT_TO_EXT_SERVER = "Connect to external servers"
    LOGIN_AS_ADMIN = "Login as admin"

    def __init__(self) -> None:
        from client import Client
        self.items = [
            MenuItem(MainMenu.CONNECT_TO_EXT_SERVER, re.compile("1"), Client.connect_to_ext_servers, self),
            MenuItem(MainMenu.LOGIN_AS_ADMIN, re.compile("2"), Client.login_as_admin, self)
        ]

    def show(self):
        for i, item in enumerate(MainMenu().items):
            print(f"{i + 1}. {item.text}")

    def parse(command):
        for item in MainMenu().items:
            item: MenuItem
            if (match := item.regex.match(command)):
                return item.handler
        return item.invalid_command()


class MenuItem:
    def __init__(self, text: str, regex: str, handler, menu) -> None:
        self.text = text
        self.regex = regex
        self.handler = handler
        self.menu = menu

    def invalid_command():
        print("Invalid Command")