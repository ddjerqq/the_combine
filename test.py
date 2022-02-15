import requests
import time
import ipfshttpclient


api = ipfshttpclient.connect("/ip4/127.0.0.1/tcp/5001/http")

if __name__ == "__main__":
    res2 = api.cat("QmSFcEpGcokZETJdE54FsrQ7XKNhV7K8zn2h1fgKgTzK9v")
    with open("res.png", "wb") as file:
        file.write(res2)
