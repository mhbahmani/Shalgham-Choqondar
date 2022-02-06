import socket
from hashlib import sha256
import threading

BUFF_SIZE = 1024


class ProxyServer:
    HOST: str = '127.0.0.1'
    PORT: int = 8003

    def __init__(self, server_host, server_port) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ProxyServer.HOST, ProxyServer.PORT))
        self.server.listen(1)
        self.clients_socket = dict()

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_host, server_port))

    def handle_client(self, client: socket.socket, session_id: str):
        while True:
            try:
                message = client.recv(BUFF_SIZE).decode("ascii")
                if not message:
                    break
                self.client.send(message)
            except:
                client.close()
                break

    def proxy_listener(self) -> None:
        while True:
            try:
                client, address = self.server.accept()
                session_id = sha256(bytes(f"client{address}", "utf-8")).hexdigest()[-20:]
                client.send(session_id.encode("ascii"))
                self.clients_socket[session_id] = client
                threading.Thread(target=self.handle_client, args=(client, session_id,)).start()
            except:
                break


if __name__ == '__main__':
    server_host = input("Please enter server host:\n")
    server_port = int(input("Please enter server port:\n"))
    proxy_server = ProxyServer(server_host, server_port)
    proxy_server.proxy_listener()
