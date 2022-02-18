import socket
from utils import *


SERVER_IP = "127.0.0.1"
PORT = 5050


class Client(object):
    def __init__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(0.5)

    def connect(self):
        while True:
            try:
                self._socket.connect((SERVER_IP, PORT))
            except ConnectionRefusedError:
                time.sleep(1)
            except socket.timeout:
                pass
            except Exception as e:
                print(type(e), e)

    def receive(self):
        try:
            data = self._socket.recv(1024)
            return data
        except socket.timeout:
            pass
        except Exception as e:
            print(type(e), e)


    def send(self, data: bytes):
        self._socket.send(data)

    def __close__(self):
        self._socket.close()


if __name__ == "__main__":
    client = Client()
    client.connect()
    while True:
        d = input("Enter your message: ")
        if d == "exit":
            client.send(b"exit")
            break
        client.send(d.encode())
        r = client.receive()
        if r:
            print(r.decode())
    client.__close__()
