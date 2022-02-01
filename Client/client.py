from menus import MainMenu

from passlib.hash import bcrypt
from getpass import getpass

import re


class Client:
    hasher = bcrypt.using(rounds=13)

    def __init__(self, password: str) -> None:
        self.password = password

    def main_menu_handler(self):
        MainMenu().show()
        while True:
            command = input()
            handler = MainMenu.parse(command)
            handler(self)

    def firewall_menu_handler(self):
        pass

    def messenger(self, proxy_port: int):
        pass

    def stream(self, proxy_port: int):
        pass

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
            
            server, port = match.groupdict()["server"], match.groupdict().get("port")
            if port: port = int(port)
            if server == "Shalgham": self.messenger(port)
            elif server == "Choghondar": self.stream(port)


if __name__ == "__main__":
    password = getpass("Set an admin password: ")

    client = Client(
        Client.hasher.hash(password)
    )
    client.main_menu_handler()