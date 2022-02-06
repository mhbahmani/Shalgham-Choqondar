from models import ResponseEncoder, ChatRoom, User, Response
from menus import CommandHandler

from hashlib import sha256
from passlib.hash import bcrypt

import threading
import binascii
import logging
import socket
import json
import os


BUFF_SIZE = 1024

class MessengerServer:
    hasher = bcrypt.using(rounds=13)
    server: socket.socket
    HOST: str = '127.0.0.1'
    PORT: int = 8002

    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((MessengerServer.HOST, MessengerServer.PORT))
        self.server.listen(1)
        logging.info(f"MessengerServer is listening on {MessengerServer.HOST}:{MessengerServer.PORT}")

        self.users = []
        self.online_users = {}
        self.clients_socket = {}
        self.end = False

    def signup(self, args, client: socket.socket = None):
        try:
            new_user =  User(
                username=User._is_valid_username(args[1], self.users),
                password=MessengerServer.hasher.hash(args[2])
            )
            for other_user in self.users:
                new_user.add_new_chatroom(other_user)
            self.users.append(new_user)
            return Response(201, "Signup Successful")
        except ValueError as e:
            return e

    def login(self, args, client: socket.socket):
        # try:
        username, password_hash = args[1], args[2]
        for user in self.users:
            if user.username == username and MessengerServer.hasher.verify(password_hash, user.password):
                client_session_id = binascii.hexlify(os.urandom(20)).decode()
                self.clients_socket[client_session_id] = client
                self.online_users[client_session_id] = user
                return Response(200, "Login Successful", {"session_id": client_session_id, "chatrooms": user.get_chatrooms()})
        return Response(401, "Incorrect username or password")
        # except Exception as e:
        #     logging.log(e)


    def exit(self):
        pass

    def handle_client(self, client: socket.socket, session_id: str):
        while not self.end:
            try:
                message = client.recv(BUFF_SIZE).decode("ascii")
                handler, args = CommandHandler.parse(message)
                args = list(args)
                response: Response = handler(self, args, client)
                self.send_response_to_client(client, response)
            except ValueError as e:
                self.send_message_to_client(client, e.__str__())
                continue
            # except:
            #     logging.info("Something went wrong")
            #     client.close()
            #     break

    def send_message_to_client(self, client: socket.socket, message: str):
        client.send(message.encode("ascii"))

    def send_response_to_client(self, client: socket.socket, response: Response):
        client.send(json.dumps(response, indent=4, cls=ResponseEncoder).encode("ascii"))

    def server_listener(self):
        while not self.end:
            try:
                if self.end: break
                client, address = self.server.accept()
                session_id = sha256(bytes(f"client{address}", "utf-8")).hexdigest()[-20:]
                logging.info(f"New player accepted with id {session_id}")
                client.send(session_id.encode("ascii"))
                self.clients_socket[session_id] = client
                threading.Thread(target=self.handle_client, args=(client, session_id,)).start()
            except:
                break

class ProxyServer:
    def __init__(self) -> None:
        pass

    def proxy(self):
        pass


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level={
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            }['INFO'])
    server = MessengerServer()
    server.signup(["signup", "a", "a"])
    server.signup(["signup", "aa", "aa"])
    server.server_listener()
    server.server.close()