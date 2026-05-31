import json
import socket


class UdpSender:
    def __init__(self, host: str, port: int = 5005):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: dict):
        message = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.sock.sendto(message, (self.host, self.port))
    