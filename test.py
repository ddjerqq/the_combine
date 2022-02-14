import requests
import time


def test_get_request():
    url = "https://app.traitsniper.com/killergf"
    r = requests.get(url)
    print(r.text)


if __name__ == "__main__":
    test_get_request()
