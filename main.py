import os
import json
import time
import requests
import threading
import sqlite3
import ipfsApi

# local
from utils import *
from headers import random_useragent

# constants
THREADS = 10  # change this to 4x your threads.
data = []
progress = 0
failed = 0


def _t_pull(start: int, amount: int, collection: str):
    global progress, failed
    for i in range(start, start+amount):
        uri = f"https://meta.hapeprime.com/{i}"

        r = requests.get(
            uri,
            headers={
                "user-agent": random_useragent()
            }
        )
        if r.status_code != 200:
            # rgb(str(r.status_code), "#ff0000")
            failed += 1
            progress += 1
            continue

        progress += 1
        # TODO CONVERT TO SQLITE
        data.append(r.json())


def get_collection_data(collection: str, number_of_items: int):
    amount = round(number_of_items / THREADS)
    threads = []
    for start in range(0, THREADS+1):
        # handle leftover amounts
        if start == THREADS:
            thread = threading.Thread(
                target = _t_pull,
                args = (start * amount, amount + round(number_of_items % THREADS), collection)
            )
        else:
            thread = threading.Thread(
                target=_t_pull,
                args=(start * amount, amount, collection)
            )
        threads.append(thread)
        thread.start()


def _t_progress_ticker(total: int):
    while True:
        rgb(
            f"\r[+] {progress:<5}/ {total} | failed: {failed} | {round((progress / total) * 100, 2)}%",
            "#00ff00",
            newline=False
        )
        if progress >= total:
            break


def setup():
    os.system("clear || cls")
    if not os.path.isdir("data"):
        os.mkdir("data")
    welcome_screen()


def main():
    global data
    setup()

    rgb("[?] Enter collection's name/ipfs id", "#ffff00", newline=False)
    collection_name = input(" > ")
    rgb("[?] Enter number of items you want to pull", "#ffff00", newline=False)
    number_of_items = int(input(" > "))
    time_start = time.time()
    rgb("[+] Started pulling data", "#00ff00")
    rgb(f"[+] Threads: {THREADS} | Amount per Thread {round(number_of_items / THREADS)}", "#00ff00")

    try:
        # we need "try" to save the data
        get_collection_data(collection_name, number_of_items)
        counter = threading.Thread(target=_t_progress_ticker, args=(number_of_items,))
        counter.start()
        counter.join()

    except KeyboardInterrupt:
        rgb("\n[!] KeyboardInterrupt", "#ff0000")

    except Exception as e:
        rgb(f"\n[!] {e}", "#ff0000")

    finally:
        rgb(f"\n[+] {len(data) - failed} items pulled in {round(time.time() - time_start, 4)} seconds", "#00ff00")
        if failed > 0:
            rgb(f"[-] {failed} items failed", "#ff0000")

        data = sorted(data, key=lambda x: int(x["name"].split("#")[1]))

        with open(f"data\\{collection_name}.json", "w") as f:
            json.dump(
                data,
                f,
                indent=4,
            )


if __name__ == "__main__":
    main()
