import json
from types import SimpleNamespace
from models import Response
from menus import MainMenu, MessengerMenu

from passlib.hash import bcrypt
from getpass import getpass

import socket
import re


class Client:
    hasher = bcrypt.using(rounds=13)
    MESSENGER_SERVER_IP = "127.0.0.1"
    MESSENGER_SERVER_PORT = 8002

    STREAM_SERVER_IP = "127.0.0.1"
    STREAM_SERVER_PORT = 8002

    def __init__(self, admin_password: str) -> None:
        self.client: socket.Socket
        self.admin_password = admin_password

    def main_menu_handler(self):
        MainMenu().show()
        while True:
            command = input()
            handler, _ = MainMenu().parse(command)
            handler(self)

    def firewall_menu_handler(self):
        pass

    def messenger(self, proxy_port: int):
        self.connect(Client.MESSENGER_SERVER_IP, Client.MESSENGER_SERVER_PORT)
        print(self.session_id)
        messenger_client = MessengerClient(self.client, self.session_id)
        messenger_client.handle()

    def stream(self, proxy_port: int):
        self.connect(Client.STREAM_SERVER_IP, Client.STREAM_SERVER_PORT)
        print(self.session_id)

    def login_as_admin(self):
        while not Client.hasher.verify(getpass(), self.admin_password):
            print("Wrong admin_Password")
        self.firewall_menu_handler()

    def connect_to_ext_servers(self):
        while True:
            user_input = input()
            match = re.match("(?P<server>(Shalgham|Choghondar))( via (?P<port>\d+))?", user_input)
            if not match:
                print("Invalid Server name")
                continue
            break
            
        server, port = match.groupdict()["server"], match.groupdict().get("port")
        if port: port = int(port)
        if server == "Shalgham": self.messenger(port)
        elif server == "Choghondar": self.stream(port)

    def connect(self, address, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((address, port))
        self.session_id = self.client.recv(1024).decode('ascii')


class MessengerClient:
    def __init__(self, socket, session_id) -> None:
        self.socket = socket
        self.session_id = session_id

    def signup(self) -> None:
        while True:
            username = input("Please enter your username: ")
            password = getpass("Please enter your password: ")
            password_confirmation = getpass("Please enter your password again: ")
            if password != password_confirmation:
                print("Passwords do not match")
                continue
            self.send_to_server(MessengerMenu.SIGNUP, [username, password])
            response = self.get_response()
            if response.status_code != 201:
                print(response.message)
                continue
            break

    def login(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def handle(self) -> None:
        MessengerMenu().show()
        while True:
            command = input()
            handler, _ = MessengerMenu().parse(command)
            handler(self)

    def send_to_server(self, command: str, args: list):
        self.socket.send(f"{self.session_id}::{command}::{'|,|'.join(args)}".encode("ascii"))

    def get_response(self) -> Response:
        res: str = self.socket.recv(1024).decode("ascii")
        return json.loads(res, object_hook=lambda d: SimpleNamespace(**d))


if __name__ == "__main__":
    admin_password = getpass("Set an admin password: ")
    # admin_password = "hello"

    client = Client(
        admin_password=Client.hasher.hash(admin_password)
    )
    client.main_menu_handler()
    # client.connect_to_ext_servers()