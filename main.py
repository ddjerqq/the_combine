import sys
import requests
import threading

# local
from utils import *
from headers import random_useragent
from database import database as db

# constants
_t_lock = threading.Lock()
THREADS = 20  # change this to 4x your threads.
Progress = 1
Failed = 0
Done = False

proxies = {"https": "http://metacircuits:dZwUllzyyZWL41U0@p.litespeed.cc:31112"}


def _t_pull(start: int, amount: int, collection_url: str, collection_name: str):
    global Progress, Failed, Done
    if Done:
        sys.exit()

    for i in range(start, start+amount):
        if not i:
            continue
            # most of the time, we don't have item 0
        if Done:
            sys.exit()

        data = None
        for _ in range(5):
            try:
                r = requests.get(
                    f"{collection_url}/{i}",
                    headers={"user-agent": random_useragent()}
                )
                if r.status_code == 200:
                    data = r.json()
                    break
                else:
                    try:
                        r2 = requests.get(
                            f"{collection_url}/{i}",
                            headers={"user-agent": random_useragent()},
                            proxies=proxies
                        )
                        if r2.status_code == 200:
                            data = r.json()
                            break
                        else:
                            time.sleep(1)
                            pass
                    except Exception as e:
                        # rgb(f"\n[!] {e}", "#ff0000")
                        time.sleep(2)
            except Exception as e:
                # rgb(f"\n[!] {e}", "#ff0000")
                time.sleep(2)

        Progress += 1
        if data is not None:
            db.add_attributes(collection_name, nft_metadata=data)
        else:
            Failed += 1

    db.__save__()


def get_collection_data(collection_url: str, number_of_items: int, collection_name: str):
    amount = round(number_of_items / THREADS)
    threads = []
    for start in range(0, THREADS+1):
        # handle leftover amounts
        if start == THREADS:
            thread = threading.Thread(
                target = _t_pull,
                args = (
                    start * amount,
                    amount + round(number_of_items % THREADS),
                    collection_url,
                    collection_name
                )
            )
        else:
            thread = threading.Thread(
                target=_t_pull,
                args=(
                    start * amount,
                    amount,
                    collection_url,
                    collection_name
                )
            )
        threads.append(thread)
        thread.start()
    return threads


def _t_progress_ticker(total: int):
    global Done
    while True:
        rgb(
            f"\r[+] {Progress:<5} / {total} | failed: {Failed} | {(Progress / total) * 100:.2f}%",
            "#00ff00",
            newline=False
        )
        if Progress >= total:
            Done = True
            break
    rgb(
        f"\r[+] {total:<5} / {total} | failed: {Failed} | 100.00%",
        "#00ff00",
        newline = False
    )


def setup():
    os.system("clear || cls")
    if not os.path.isdir("data"):
        os.mkdir("data")
    welcome_screen()


# def collection_stat(collection_name: str, limit: int = 10) -> None:
#     rarest_attributes = db.rarest_attributes(collection_name, limit=limit)
#     total = db.total_number_of_values(collection_name)
#     for rarest_attributes in rarest_attributes:
#         print(rarest_attributes)
#         for attr in db.rarest_values_of_attribute(collection_name, rarest_attributes[0], limit=limit):
#             rgb(f"{attr[0]} has {attr[1]} {attr[2]}/{total} {round((attr[2] / total) * 100, 4)}%", "#00ff00")


def main():
    setup()

    rgb("[?] Enter collection's url", "#ffff00", newline=False)
    collection_url = input(" > ")
    if collection_url.endswith("/"):
        collection_url = collection_url[:-1]

    if not collection_url:
        rgb("[!] No collection url entered! quitting!", "#ff0000")
        exit()

    rgb("[?] Enter collection name", "#ffff00", newline=False)
    collection_name = input(" > ")
    if collection_name:
        db.create_table(collection_name)
    else:
        rgb("[!] No collection name entered! quitting!", "#ff0000")
        exit()

    rgb("[?] Enter number of items you want to pull", "#ffff00", newline=False)
    number_of_items = int(input(" > "))

    time_start = time.time()
    rgb(f"[+] Started pulling data from {collection_name}", "#00ff00")
    rgb(f"[+] Threads: {THREADS} | Amount per Thread {round(number_of_items / THREADS)}", "#00ff00")

    try:
        get_collection_data(collection_url, number_of_items, collection_name)
        counter = threading.Thread(target=_t_progress_ticker, args=(number_of_items,))
        counter.start()
        counter.join()

    except KeyboardInterrupt:
        rgb("\n[!] KeyboardInterrupt", "#ff0000")

    except Exception as e:
        rgb(f"\n[!] {e}", "#ff0000")

    finally:
        db.__save__()
        rgb(f"\n[+] total pieces - {db.get_total_names(collection_name)}              \n"
            f"[+] total values - {db.get_total_values(collection_name)}             \n"
            f"[+] distinct values - {db.get_distinct_values(collection_name)}       \n"
            f"[+] distinct attributes - {db.get_total_attributes(collection_name)}  \n"
            f"[+] items pulled successfully in {round(time.time() - time_start, 2)} seconds",
            color="#00ff00"
            )
        if Failed > 0:
            rgb(
                f"[-] {Failed} items failed {round(Failed / number_of_items * 100, 2)}% of total",
                color="#ff0000"
            )


if __name__ == "__main__":
    main()
    # print(db.get_total_names("hape"))
    # https://meta.hapeprime.com/
    # hape
    # please supply exact amount of items, or else BAN
    # 8192
