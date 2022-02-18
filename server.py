import os
import json
import time
import socket
import pickle
import threading
from utils import *

from database import database as db

PORT = 5050


class Server(object):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('0.0.0.0', PORT))
        self._socket.listen(10)
        self._socket.settimeout(0.5)
        self._buffer  = 65536
        self._clients: dict[tuple[str, int], socket] = {}

    def start(self):
        self._client_acceptor()

    def _t_client_handler(self, client_socket, address):
        try:
            print(f"[+] New client connected: {address[0]}:{address[1]}")
            client_socket.send(b"Welcome to the server!")
            while True:
                msg = self._socket.recv(self._buffer)
                if not msg:
                    continue

                print(f"[<] {address[0]}:{address[1]} -> {msg.decode()}")
                client_socket.send(msg)

                if msg == b"exit":
                    client_socket.close()
                    self._clients.pop(address)
        except socket.timeout:
            pass


    def _client_acceptor(self):
        # crash the server with keyboard interrupt
        try:
            while True:
                try:
                    client_socket, address = self._socket.accept()
                    self._clients[(address[0], address[1])] = client_socket
                    t = threading.Thread(target=self._t_client_handler, args=(client_socket, address))
                    t.start()
                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            self.__close__()


    def __close__(self):
        rgb("[-] Closing server...", color=0xffff00)
        for client in self._clients:
            # TODO try close, except socket.error
            self._clients[client].close()
            rgb(f"[-] Client {client[0]}:{client[1]} disconnected", color=0xffff00)
        self._socket.close()
        rgb("[-] Server closed", color=0xffff00)


if __name__ == "__main__":
    rgb("[+] Server starting...", color=0xffff00)
    server = Server()
    server.start()

