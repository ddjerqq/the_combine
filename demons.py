import requests.exceptions

from utils import *
from database import database as db


MAX_THREADS = 64


class TPuller(threading.Thread):
    Progress = 1
    Die = False
    Total = None

    def __init__(self, start: int, amount: int, collection_uri: str, collection_name: str, json_at_the_end: bool):
        threading.Thread.__init__(self)
        self._start = start
        self._amount = amount
        self._collection_uri = collection_uri
        self._collection_name = collection_name
        self._json_at_the_end = json_at_the_end

    def run(self):
        for idx in range(self._start, self._start + self._amount):
            proxy_needed = False
            while True:
                if TPuller.Die:
                    sys.exit()

                try:
                    r = requests.get(
                        f"{self._collection_uri}/{idx}.json" if self._json_at_the_end else f"{self._collection_uri}/{idx}",
                        headers={"user-agent": random_useragent()},
                        proxies=PROXY if proxy_needed else None,
                    )

                    match r.status_code:
                        case 404:
                            if idx > 0:
                                sys.exit()
                        case 200:
                            data = r.json()
                            break
                        case _:
                            # TODO fix
                            time.sleep(0.1)
                            proxy_needed = True

                except requests.exceptions.ProxyError:
                    proxy_needed = True
                except Exception as exc:
                    proxy_needed = True

            TPuller.Progress += 1

            db.add_attributes(data)

    @staticmethod
    def _t_counter():
        _start_time = time.time()
        progresses = []
        while TPuller.Progress <= TPuller.Total:
            _time_now = time.time()
            rgb(
                f"\r[+] #{TPuller.Progress:<4} | "
                f"{round((TPuller.Progress + 1) / TPuller.Total * 100, 2):<5}% | "
                f"Time elapsed: {round(_time_now - _start_time, 2):<6} | "
                f"Time average: {(_time_now - _start_time) / (TPuller.Progress + 1):.3f}",
                0x00ff00,
                newline=False
            )

            # CHECK IF NO NEW DATA IS BEING SENT
            progresses.append(TPuller.Progress)
            #                    66 here means if we have been stuck for 66 * 0.015 seconds
            if len(progresses) > 66:
                progresses = progresses[1:]
            if len(progresses) == 66 and progresses[-1] == progresses[0]:
                TPuller.Die = True
                break
            time.sleep(0.15)

    @staticmethod
    def start_counter():
        t = threading.Thread(target=TPuller._t_counter)
        t.start()
        t.join()

    @staticmethod
    def _t_downloader(item_name: str, url: str, collection_name: str):
        proxy_needed = False
        data = None
        while True:
            try:
                r = requests.get(
                    url,
                    headers={"user-agent": random_useragent()},
                    proxies=PROXY if proxy_needed else None
                )
                if r.status_code == 200:
                    data = r.content
                    break
                else:
                    continue
            except ConnectionError or requests.exceptions.ProxyError:
                proxy_needed = True
                continue

        # create folder if not exists
        if not os.path.exists(f"{ABSOLUTE_PATH}\\images\\{collection_name}"):
            os.makedirs(f"{ABSOLUTE_PATH}\\images\\{collection_name}")

        with open(f"{ABSOLUTE_PATH}\\images\\{collection_name}\\{item_name}.png", "wb") as img:
            img.write(data)

    @staticmethod
    def downloader(*items: str, collection_name: str):
        rgb("[+] Downloading images...", 0x00ff00, newline=False)
        downloaders = []
        for item in items:
            url = db.get_image_url(item)
            if url:
                if "ipfs://" in url:
                    url = url.replace("ipfs://", "https://ipfs.io/ipfs/")

                t = threading.Thread(target=TPuller._t_downloader, args=(item, url, collection_name))
                t.start()
                downloaders.append(t)

        for t in downloaders:
            t.join()

        rgb("\r[+] Done                 ", 0x00ff00)


def spawn_demons(collection_uri: str, collection_name: str, number_of_items: int, json_at_the_end: bool):
    amount, remainder = divmod(number_of_items, MAX_THREADS)
    amounts = [amount + 1 if n < remainder else amount for n in range(MAX_THREADS)]

    TPuller.Total = number_of_items

    for idx, amount in enumerate(amounts):
        t = TPuller(idx * amount, amount, collection_uri, collection_name, json_at_the_end)
        t.start()

    g = 0x00ff00
    r = 0xff0000
    rgb(f"\r[+] Started pulling ", color=g, newline=False)
    rgb(f"{number_of_items} ", color=r, newline=False)
    rgb(f"items from ", color=g, newline=False)
    rgb(f"{collection_name} ", color=r, newline=False)
    rgb(f"with ", color=g, newline=False)
    rgb(f"{MAX_THREADS} ", color=r, newline=False)
    rgb(f"threads from ", color=g, newline=False)
    rgb(f"{collection_uri}", color=r)

    TPuller.start_counter()



