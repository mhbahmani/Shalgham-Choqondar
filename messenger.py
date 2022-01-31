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

    def signup(self):
        pass

    def login(self):
        pass

    def exit(self):
        pass

    def handle_input(self):
        pass
    
    def run_server(self):
        pass


class ProxyServer:
    def __init__(self) -> None:
        pass

    def proxy(self):
        pass