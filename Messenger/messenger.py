from models import ResponseEncoder, ChatRoom, User, Response
from menus import CommandHandler

from hashlib import sha256
from passlib.hash import bcrypt

import threading
import selectors
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
    PORT: int = 8001

    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(False)
        self.server.bind((MessengerServer.HOST, MessengerServer.PORT))
        self.server.listen(1)

        logging.info(f"MessengerServer is listening on {MessengerServer.HOST}:{MessengerServer.PORT}")
        
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.server, selectors.EVENT_READ, self.accept)

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
            return Response(400, "Username is not available")

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

    def open_chatroom(self, args, client: socket.socket):
        try:
            session_id, contact_username = args[0], args[1]
            user = self.online_users.get(session_id)
            if not user: return Response(401, "You are not logged in")
            chatroom: ChatRoom = user.chatrooms.get(contact_username)
            if not chatroom: return Response(401, "Chatroom not found")
            return Response(200, "Chatroom opened", {"chatroom": chatroom.get_messages()})
        except Exception as e:
            logging.info(e)

    def send_message(self, args, client: socket.socket):
        try:
            session_id, contact_username, message = args[0], args[1], args[2]
            user = self.online_users.get(session_id)
            if not user: return Response(401, "You are not logged in")
            chatroom: ChatRoom = user.chatrooms.get(contact_username)
            if not chatroom: return Response(401, "Chatroom not found")
            chatroom.add_message(message)
            return Response(200, "Message sent")
        except Exception as e:
            logging.info(e)

    def update_chatroom(self, args, client: socket.socket):
        try:
            session_id, contact_username = args[0], args[1]
            user = self.online_users.get(session_id)
            if not user: return Response(401, "You are not logged in")
            chatroom: ChatRoom = user.chatrooms.get(contact_username)
            if not chatroom: return Response(401, "Chatroom not found")
            return Response(200, "Chatroom Updated", {"chatroom": chatroom.get_unread_messages()})
        except Exception as e:
            logging.info(e)

    def get_chatrooms(self, args, client: socket.socket):
        session_id = args[0]
        user = self.online_users.get(session_id)
        if not user: return Response(401, "You are not logged in")
        return Response(200, "Login Successful", {"chatrooms": user.get_chatrooms()})

    def get_x_last_messages(self, args, client):
        session_id, contact_username, num_messages = args[0], args[1], int(args[2])
        user = self.online_users.get(session_id)
        if not user: return Response(401, "You are not logged in")
        chatroom: ChatRoom = user.chatrooms.get(contact_username)
        if not chatroom: return Response(401, "Chatroom not found")
        return Response(200, "Messages Fetched", {"messages": chatroom.get_messages(num_messages)})
    def exit(self):
        pass

    def read(self, client):
        try:
            message = client.recv(BUFF_SIZE).decode("ascii")
            logging.debug(f"Received message: {message}")
            if message:
                handler, args = CommandHandler.parse(message)
                args = list(args)
                response: Response = handler(self, args, client)
                self.send_response_to_client(client, response)
            else:
                logging.info("Closing connection")
                self.selector.unregister(client)
                client.close()
        except Exception as e:
            logging.info(e)
            self.selector.unregister(client)
            client.close()

    # Used in old blocking method
    # def handle_client(self, client: socket.socket, session_id: str):
    #     while not self.end:
    #         try:
    #             message = client.recv(BUFF_SIZE).decode("ascii")
    #             handler, args = CommandHandler.parse(message)
    #             args = list(args)
    #             response: Response = handler(self, args, client)
    #             self.send_response_to_client(client, response)
    #         except ValueError as e:
    #             self.send_message_to_client(client, e.__str__())
    #             continue
    #         # except:
    #         #     logging.info("Something went wrong")
    #         #     client.close()
    #         #     break

    def send_message_to_client(self, client: socket.socket, message: str):
        client.send(message.encode("ascii"))

    def send_response_to_client(self, client: socket.socket, response: Response):
        client.send(json.dumps(response, indent=4, cls=ResponseEncoder).encode("ascii"))

    def non_blocking_server_listener(self):
        while not self.end:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                callback = key.data
                logging.debug(f"Callback: {callback}")
                print(key.fileobj)
                callback(key.fileobj)

    def accept(self, server_socket):
        client, address = server_socket.accept()
        client.setblocking(False)
        session_id = sha256(bytes(f"client{address}", "utf-8")).hexdigest()[-20:]
        logging.info(f"New player accepted with id {session_id}")

        client.send(session_id.encode("ascii"))
        self.clients_socket[session_id] = client
        self.selector.register(client, selectors.EVENT_READ, self.read)

    # Used in old blocking method
    # def server_listener(self):
    #     while not self.end:
    #         try:
    #             if self.end: break
    #             client, address = self.server.accept()
    #             session_id = sha256(bytes(f"client{address}", "utf-8")).hexdigest()[-20:]
    #             logging.info(f"New player accepted with id {session_id}")
    #             client.send(session_id.encode("ascii"))
    #             self.clients_socket[session_id] = client
    #             threading.Thread(target=self.handle_client, args=(client, session_id,)).start()
    #         except:
    #             break

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
    server.signup(["signup", "aaa", "aaa"])
    # server.server_listener()
    server.non_blocking_server_listener()
    server.server.close()