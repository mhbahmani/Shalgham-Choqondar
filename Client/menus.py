from meta import SingletonMeta

import re


class Menu():
    def show(self):
        for i, item in enumerate(self.items):
            print(f"{i + 1}. {item.text}")

    def parse(self, command):
        for item in self.items:
            item: MenuItem
            if (match := item.regex.match(command)):
                return item.handler
        return MenuItem.invalid_command


class MainMenu(Menu, metaclass=SingletonMeta):
    CONNECT_TO_EXT_SERVER = "Connect to external servers"
    LOGIN_AS_ADMIN = "Login as admin"

    def __init__(self) -> None:
        from client import Client
        self.items = [
            MenuItem(MainMenu.CONNECT_TO_EXT_SERVER, re.compile("1"), Client.connect_to_ext_servers, self),
            MenuItem(MainMenu.LOGIN_AS_ADMIN, re.compile("2"), Client.login_as_admin, self)
        ]
        super().__init__()


class MessengerMenu(Menu, metaclass=SingletonMeta):
    SIGNUP = "Signup"
    LOGIN = "Login"
    EXIT = "Exit"

    def __init__(self) -> None:
        from client import MessengerClient
        self.items = [
            MenuItem(MessengerMenu.SIGNUP, re.compile("1"), MessengerClient.signup, self),
            MenuItem(MessengerMenu.LOGIN, re.compile("2"), MessengerClient.login, self),
            MenuItem(MessengerMenu.EXIT, re.compile("3"), MessengerClient.login, self)
        ]
        super().__init__()


class MenuItem:
    def __init__(self, text: str, regex: str, handler, menu) -> None:
        self.text = text
        self.regex = regex
        self.handler = handler
        self.menu = menu

    def invalid_command(self):
        print("Invalid Command")