from menus import CommandHandler

from hashlib import sha256

import threading
import logging
import socket
import re
import cv2

BUFF_SIZE = 1024

class StreamerServer:
    server: socket.socket
    HOST: str = '127.0.0.1'
    PORT: int = 8002

    FINISH_STREAMING = "FINISH_STREAMING"

    def __init__(self) -> None:
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((StreamerServer.HOST, StreamerServer.PORT))
        self.server.listen(1)
        logging.info(f"StreamerServer is listening on {StreamerServer.HOST}:{StreamerServer.PORT}")

        self.users: list = []
        self.clients_socket = {}
        self.end = False

    @staticmethod
    def stream_video(udp_socket: socket.socket, udp_port: int, video_delay: float, video_path: str, b: bool):
        cap = cv2.VideoCapture(video_path)
        while cap.isOpened():
            if not True:
                break
            try:
                ret, photo = cap.read()
                # cv2.imshow('Video Streamer', photo)
                ret, buffer = cv2.imencode(".jpg", photo, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
                x_as_bytes = pickle.dumps(buffer)
                udp_socket.sendto(x_as_bytes, (localhost, udp_port))
                sleep(video_delay)
            except Exception as e:
                byte_message = bytes(UDP_STREAMING_FINISH, "utf-8")
                for i in range(500):
                    udp_socket.sendto(byte_message, (localhost, udp_port))
                udp_socket.close()

                break

        # cv2.destroyAllWindows()
        cap.release()

    def handle_client(self, client: socket.socket, session_id: str):
        while not self.end:
            try:
                message = client.recv(BUFF_SIZE).decode("ascii")
                if message == StreamerServer.FINISH_STREAMING:
                    self.end = True
                    break
            except AttributeError:
                pass
            except ValueError:
                logging.error("Something bad happend")
                client.close()
                break
        client.close()    

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



if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level={
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            }['INFO'])
    ss = StreamerServer()
    ss.server_listener()
    StreamerServer.stream_video(udp_socket=ss.server, 
                                udp_port=StreamerServer.PORT, 
                                video_delay=1, 
                                video_path='videos/sare_keyfi_aziz.mp4', 
                                b=False)
        