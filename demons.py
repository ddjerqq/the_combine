import threading
from utils import *
from database import database as db

MAX_THREADS = 32


class TPuller(threading.Thread):
    Progress = 0
    Total = None
    Done = False

    def __init__(self, start: int, amount: int, collection_uri: str, collection_name: str):
        threading.Thread.__init__(self)
        self._start = start
        self._amount = amount
        self._collection_uri = collection_uri
        self._collection_name = collection_name


    def run(self):
        for i in range(self._start, self._start + self._amount):
            proxy_needed = False
            while True:
                try:
                    r = requests.get(
                        f"{self._collection_uri}/{i}",
                        headers={"user-agent": random_useragent()},
                        proxies=PROXY if proxy_needed else None,
                    )
                    if r.status_code in [404, 400]:
                        sys.exit()
                    elif r.status_code == 200:
                        data = r.json()
                        break
                    else:
                        proxy_needed = True

                except requests.exceptions.ProxyError or ConnectionError or requests.exceptions.SSLError:
                    rgb(f"\n[!] Proxy error, connection timed out, or SSL error", "#ff0000")
                    time.sleep(1)
                except Exception as ex:
                    rgb(f"\n[!!!RUFFIAN!!!] {type(ex)} {ex}", "#ff0000")
                    time.sleep(1)

            TPuller.Progress += 1
            db.add_attributes(self._collection_name, data)


    @staticmethod
    def _counter():
        start_time = time.time()
        while TPuller.Progress <= TPuller.Progress:
            time_now = time.time()
            rgb(
                f"\r[+] #{TPuller.Progress:<5} | "
                f"{(TPuller.Progress / TPuller.Total) * 100:.2f}% | "
                f"time elapsed: {time_now - start_time:.2f} | "
                f"avg time: {(time_now - start_time) / TPuller.Progress:.2f}",
                "#00ff00",
                newline = False
            )
            time.sleep(0.1)
        else:
            print()


    @staticmethod
    def start_counter():
        t = threading.Thread(target=TPuller._counter)
        t.start()
        t.join()



def spawn_demons(collection_uri: str, collection_name: str, number_of_items: int):
    amount, remainder = divmod(number_of_items, MAX_THREADS)
    amounts = [amount + 1 if n < remainder else amount for n in range(MAX_THREADS)]

    for idx, amount in enumerate(amounts):
        t = TPuller(idx, amount, collection_uri, collection_name)
        t.start()

    rgb(
        f"[+] Started pulling {number_of_items} from {collection_name} with {MAX_THREADS} threads",
        0x00ff00
    )

    TPuller.start_counter()




if __name__ == "__main__":
    spawn_demons("https://gateway.pinata.cloud/ipfs/QmdkYWDquJ8Bfa8zLwSa5553HWdBvTrAnM7GEkHdeiUJry", "test", 679)
    # puller.pull()
