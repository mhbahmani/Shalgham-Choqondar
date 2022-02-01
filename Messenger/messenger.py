from menus import CommandHandler

from hashlib import sha256

import threading
import logging
import socket


class MessengerServer:
    server: socket.socket
    HOST: str = '127.0.0.1'
    PORT: int = 8001

    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((MessengerServer.HOST, MessengerServer.PORT))
        self.server.listen(1)
        logging.info(f"MessengerServer is listening on {MessengerServer.HOST}:{MessengerServer.PORT}")

        self.users: list = []
        self.end = False

    def signup(self):
        pass

    def login(self):
        pass

    def exit(self):
        pass

    def handle_client(self, client: socket.socket, session_id: str):
        while not self.end:
            try:
                command = input()
                handler = CommandHandler.parse(command)
                handler(self)
            except AttributeError:
                pass
            except ValueError:
                logging.error("Something bad happend")
                client.close()
                break    

    def run_server(self):
        pass

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
    server.server_listener()
    server.server.close()