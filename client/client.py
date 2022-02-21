"""
This client should run in the background and listen for messages from the server.

"""

import json
import socket
import pickle
import typing
from utils import *


SERVER_IP = "127.0.0.1"
PORT = 5050
# CHANGE THIS
THREADS = 64
CORES = 4


class Client(object):
    @staticmethod
    def _payloadify(data: typing.Any) -> bytes:
        """
        Payloadify Any data and get bytes of a json.\n
        :param data: Any
        :return: bytes of this data inside a json {"data": data}
        """
        data = {"data": data}
        data = json.dumps(data)
        data = pickle.dumps(data)
        return data


    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(0.5)

    def connect(self):
        while True:
            try:
                self._socket.connect((SERVER_IP, PORT))
                self._socket.send(Client._payloadify({"cores": CORES, "threads": THREADS}))
                break
            except ConnectionRefusedError:
                time.sleep(1)
            except socket.timeout:
                pass
            except Exception as e:
                print(type(e), e)

        while True:
            try:
                data = self._socket.recv(1024)
                print(data.decode())
            except ConnectionRefusedError:
                time.sleep(1)
            except ConnectionResetError:
                break
            except socket.timeout:
                pass
            except Exception as e:
                print(type(e), e)



    def __close__(self):
        self._socket.close()


if __name__ == "__main__":
    client = Client()
    client.connect()
    client.__close__()
