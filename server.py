import json
import socket
import pickle
from utils import *

PORT = 5050


class Server(object):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.bind(('0.0.0.0', PORT))
        self._socket.listen(10)
        self._buffer  = 65536
        self._clients: dict[tuple[str, int], socket] = {}
        self._stop_accepting = False


    def start(self):
        self._client_acceptor()


    def execute(self):
        self._stop_accepting = True


    def _t_client_handler(self, client_socket, address):
        coresthreads = client_socket.recv(self._buffer)
        coresthreads = pickle.loads(coresthreads)
        coresthreads = json.loads(coresthreads)
        self._clients[(address[0], address[1])]["cores"] = coresthreads["data"]["cores"]
        self._clients[(address[0], address[1])]["threads"] = coresthreads["data"]["threads"]
        print(self._clients)

        # pause exec
        while not self._stop_accepting:
            pass

        # determine how much we want the socket to pull
        client_socket.send(b"pull me 10 items")


    def _client_acceptor(self):
        try:
            while not self._stop_accepting:
                try:
                    # blocking line
                    client_socket, address = self._socket.accept()
                    self._clients[(address[0], address[1])] = {"socket": client_socket}
                    t = threading.Thread(target=self._t_client_handler, args=(client_socket, address))
                    t.start()
                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            self.__close__()

    def __close__(self):
        rgb("[-] Closing server...", color=0xffff00)
        for client in self._clients:
            self._clients[client].close()
            rgb(f"[-] Client {client[0]}:{client[1]} disconnected", color=0xffff00)
        self._socket.close()
        rgb("[-] Server closed", color=0xffff00)


if __name__ == "__main__":
    rgb("[+] Server starting...", color=0x00ff00)
    server = Server()
    server.start()

