import threading

import requests.exceptions

from utils import *
from database import database as db

MAX_THREADS = 64


class TPuller(threading.Thread):
    Progress = 1
    Total = None


    def __init__(self, start: int, amount: int, collection_uri: str, collection_name: str, json_at_the_end: bool):
        threading.Thread.__init__(self)
        self._start = start
        self._amount = amount
        self._collection_uri = collection_uri
        self._collection_name = collection_name
        self._json_at_the_end = json_at_the_end


    def run(self):
        for i in range(self._start, self._start + self._amount):
            proxy_needed = False
            while True:
                try:
                    r = requests.get(
                        f"{self._collection_uri}/{i}.json" if self._json_at_the_end else f"{self._collection_uri}/{i}",
                        headers={"user-agent": random_useragent()},
                        proxies=PROXY if proxy_needed else None,
                    )
                    if r.status_code == 404:
                        if i > 0:
                            sys.exit()
                    elif r.status_code == 200:
                        data = r.json()
                        break
                    else:
                        proxy_needed = True
                except KeyboardInterrupt:
                    sys.exit()
                except Exception:
                    proxy_needed = True

            TPuller.Progress += 1

            db.add_attributes(data)


    @staticmethod
    def _counter():
        _start_time = time.time()
        # FIXME this is not working
        while TPuller.Progress < TPuller.Total * 0.95:
            _time_now = time.time()
            rgb(
                f"\r[+] #{TPuller.Progress:<4} | "
                f"{round((TPuller.Progress + 1) / TPuller.Total * 100, 2):<5}% | "
                f"{round(_time_now - _start_time, 2):<6}S | "
                f"avg {(_time_now - _start_time) / (TPuller.Progress + 1):.3f}",
                "#00ff00",
                newline=False
            )
            time.sleep(0.05)
        else:
            print()


    @staticmethod
    def start_counter():
        t = threading.Thread(target=TPuller._counter)
        t.start()
        t.join()


def spawn_demons(collection_uri: str, collection_name: str, number_of_items: int, json_at_the_end: bool):
    amount, remainder = divmod(number_of_items, MAX_THREADS)
    amounts = [amount + 1 if n < remainder else amount for n in range(MAX_THREADS)]

    TPuller.Total = number_of_items

    for idx, amount in enumerate(amounts):
        t = TPuller(idx * amount, amount, collection_uri, collection_name, json_at_the_end)
        t.start()

    rgb(
        f"\r[+] Started pulling {number_of_items - 1} from {collection_name} with {MAX_THREADS} threads",
        0x00ff00
    )

    TPuller.start_counter()


if __name__ == "__main__":
    spawn_demons("https://gateway.pinata.cloud/ipfs/QmdkYWDquJ8Bfa8zLwSa5553HWdBvTrAnM7GEkHdeiUJry", "test", 679, True)
    # puller.pull()
