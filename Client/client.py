from menus import ChatroomMenu
from models import Response, ResponseDecoder
from menus import MainMenu, MessengerMenu

from passlib.hash import bcrypt
from getpass import getpass

import pickle

import threading
import socket
import json
import time
import re

STREAMING_FINISH = "STREAMING_FINISH"

class Client:
    hasher = bcrypt.using(rounds=13)
    MESSENGER_SERVER_IP = "127.0.0.1"
    MESSENGER_SERVER_PORT = 8001

    STREAM_SERVER_IP = "127.0.0.1"
    STREAM_SERVER_PORT = 8002

    UDP_PORT = 8003

    BUFFER_SIZE = 100000000

    def __init__(self, admin_password: str) -> None:
        self.client: socket.Socket
        self.session_id: str
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
        udp_client, _ = self.make_udp_connection()
        udp_client.connect((self.STREAM_SERVER_IP, self.UDP_PORT))
        while True:
            print(udp_client)
            x = udp_client.recvfrom(Client.BUFFER_SIZE)
            data = x[0]
            print(data)
            if len(data) < 100:
                if data.decode('utf-8') == STREAMING_FINISH:
                    self.send_message(STREAMING_FINISH)
                    break
            data = pickle.loads(data)
            data = cv2.imdecode(data, cv2.IMREAD_COLOR)
            cv2.imshow('Video Streamer (client-side)', data)
            print(data)
            if cv2.waitKey(10) == 13:  # Press Enter then window will close
                self.send_message(STREAMING_FINISH)
                break
        cv2.destroyAllWindows()

    def send_message(self: "Client", message: str):
        self.udp_client.send(message.encode('ascii'))

    def login_as_admin(self):
        while not Client.hasher.verify(getpass(), self.admin_password):
            print("Wrong admin_Password")
        self.firewall_menu_handler()

    def connect_to_ext_servers(self):
        while True:
            # user_input = "Shalgham"
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

    def connect_udp(self, address, port):
        self.udp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_client.connect((address, port))
        return self.udp_client

    def make_udp_connection(self):
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind((Client.STREAM_SERVER_IP, Client.UDP_PORT))
        port = udp_server.getsockname()[1]
        # send_message(self, UDP_PORT_INFO_MESSAGE + ' ' + str(port))
        return udp_server, port



class MessengerClient:
    def __init__(self, socket, session_id) -> None:
        self.socket = socket
        self.session_id = session_id
        self.chatrooms: dict
        self.close_chatroom = False

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
        username = input("Please enter your username: ")
        password = getpass("Please enter your password: ")
        self.send_to_server(MessengerMenu.LOGIN, [username, password])
        response = self.get_response()
        if response.status_code != 200:
            print(response.message)
            return
        self.session_id = response.data["session_id"]
        self.chatrooms = response.data["chatrooms"]
        self.messenger()

    def messenger(self):
        while True:
            self.show_chatrooms()
            username = input()
            if self.chatrooms.get(username) != None:
                self.send_to_server(ChatroomMenu.OPEN_CHATROOM, [username])
                response = self.get_response()
                if response.status_code != 200:
                    print(response.message)
                self.handle_chatroom(response.data["chatroom"], username)
            self.close_chatroom = False
            self.update_chatrooms_list()
    

    def handle_chatroom(self, messages: str, contact: str):
        print("------------------------------")
        print(messages)
        read_thread = threading.Thread(target=self.handle_read, args=(contact,))
        read_thread.start()

        write_thread = threading.Thread(target=self.handle_write, args=(contact,))
        write_thread.start()
        write_thread.join()

    def exit(self) -> None:
        pass

    def handle(self) -> None:
        while True:
            MessengerMenu().show()
            command = input()
            handler, _ = MessengerMenu().parse(command)
            handler(self)

    def handle_write(self, contact: str):
        while not self.close_chatroom:
            try:
                message = input()
                if message.startswith("/"):
                    if message == "/exit":
                        self.close_chatroom = True
                        break
                    elif (match := re.match("/load (?P<x>\d+)", message)):
                        x = match.groupdict()["x"]
                        self.send_to_server(ChatroomMenu.GET_X_LAST_MESSAGES, [contact, x])
                        response = self.get_response()
                        print(response.data["messages"])
                else: 
                    self.send_to_server(ChatroomMenu.SEND_MESSAGE, [contact, message])
                    response = self.get_response()
                if response.status_code != 200:
                    continue
            except:
                break
        
    def handle_read(self, contact: str):
        while not self.close_chatroom:
            try:
                time.sleep(5)
                self.send_to_server(ChatroomMenu.UPDATE_CHATROOM, [contact])
                response = self.get_response()
                if response.status_code != 200:
                    print(response.message)
                    continue
                if len(response.data["chatroom"]) != 0:
                    print(response.data["chatroom"])
            except:
                print("read thread is dead")
                break

    def send_to_server(self, command: str, args: list):
        self.socket.send(f"{self.session_id}::{command}::{'|,|'.join(args)}".encode("ascii"))

    def get_response(self) -> Response:
        res: str = self.socket.recv(1024).decode("ascii")
        return json.loads(res, object_hook=ResponseDecoder.decode)

    def update_chatrooms_list(self):
        self.send_to_server(ChatroomMenu.UPDATE_CHATROOMS_LIST, [])
        response = self.get_response()
        if response.status_code != 200:
            print(response.message)
        self.chatrooms = response.data["chatrooms"]

    def show_chatrooms(self):
        for username in self.chatrooms:
            print(username, f"{f'({self.chatrooms[username]})' if self.chatrooms[username] else ''}")


if __name__ == "__main__":
    admin_password = getpass("Set an admin password: ")

    client = Client(
        admin_password=Client.hasher.hash(admin_password)
    )
    client.main_menu_handler()
