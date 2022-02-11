import requests
import time


def test_get_request():
    url = "https://httpbin.org/ip"
    r = requests.get(
        url,
        proxies={
            "https": "http://metacircuits:dZwUllzyyZWL41U0@p.litespeed.cc:31112"
        }
    )
    print(r.json()["origin"])


if __name__ == "__main__":
    for i in range(10):
        test_get_request()
