import sys
import argparse
import requests
import threading

# local
from utils import *
from headers import random_useragent
from database import database as db

# Globals
_t_lock = threading.Lock()
# THIS IS DEFAULT VALUE, CAN BE CHANGED BY CLI ARGS
THREADS = 20  # change this to 4x your threads.
Progress = 1
Failed = 0
Done = False


arg_parser = argparse.ArgumentParser(description="FNRC - Feggz NFT Rarity Calculator")
arg_parser.add_argument("-n", "--collection-name",
                        help="Name of collection to use", type=str, default=None)

arg_parser.add_argument("-s", "--skip",
                        help="whether to skip fetching data or not", type=bool, default=False)

arg_parser.add_argument("-u", "--url",
                        help="URL of the metadata, it should be a url which supports url/1 url/2 url/3 url/4",
                        type=str, default=None)

arg_parser.add_argument("-c", "--count",
                        help="Amount of items in a collection", type=int, default=None)

arg_parser.add_argument("-t", "--threads",
                        help="Number of threads to use", type=int, default=THREADS)

args = vars(arg_parser.parse_args())


proxy = {"https": "http://metacircuits:dZwUllzyyZWL41U0@p.litespeed.cc:31112"}


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
        while data is None:
            try:
                r = requests.get(
                    f"{collection_url}/{i}",
                    headers={"user-agent": random_useragent()}
                )
                if r.status_code == 404:
                    sys.exit()
                if r.status_code == 200:
                    data = r.json()
                else:
                    try:
                        r2 = requests.get(
                            f"{collection_url}/{i}",
                            headers={"user-agent": random_useragent()},
                            proxies=proxy
                        )
                        if r2.status_code == 200:
                            data = r.json()
                        else:
                            time.sleep(0.5)
                    except Exception as e:
                        # rgb(f"\n[!] {e}", "#ff0000")
                        time.sleep(0.5)
            except Exception as e:
                # rgb(f"\n[!] {e}", "#ff0000")
                time.sleep(0.5)

        Progress += 1
        if data is not None:
            db.add_attributes(collection_name, nft_metadata=data)
        else:
            Failed += 1

    db.__save__()


def get_collection_data(collection_url: str, number_of_items: int, collection_name: str):
    amount = round(number_of_items / THREADS)
    threads = []
    for start in range(0, THREADS):
        # handle leftover amounts
        # TODO make modulo spread around the threads,
        # if the remainder is 56 then each thread will get 56 / threads
        # and the remainder will be given to the last one
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


def _t_progress_ticker(total: int, start_time: float):
    global Done
    while True:
        time_now = time.time()
        rgb(
            f"\r[+] {Progress:<5} / {total} | "
            f"failed: {Failed} | "
            f"time elapsed: {time_now - start_time:.2f} | "
            f"done: {(Progress / total) * 100:.2f}% | "
            f"time per item: {(time_now - start_time) / Progress:.2f}",
            "#00ff00",
            newline=False
        )
        if Progress >= total:
            Done = True
            break
        time.sleep(0.05)
    rgb(
        f"\r[+] {total:<5} / {total} | "
        f"failed: {Failed} | "
        f"time elapsed: {time.time() - start_time:.2f} | "
        f"done: 100.00%",
        f"time per item: {(time_now - start_time) / Progress:.2f}"
        "#00ff00",
        newline = False
    )


def setup():
    os.system("clear || cls")
    if not os.path.isdir("data"):
        os.mkdir("data")
    welcome_screen()


def main(
        collection_url: str = None,
        collection_name: str = None,
        number_of_items: int = None,
        skip_fetch: bool = False
        ) -> None:
    """
    Main function.
    optionally pass the parameters, otherwise they will be prompted.
    :param collection_url: default None
    :param collection_name: default None
    :param number_of_items: default None
    :param skip_fetch: default False
    :return: None
    """

    if collection_url and collection_url.endswith("/"):
        collection_url = collection_url[:-1]

    if not collection_url:
        rgb("[?] Enter collection's url", "#ffff00", newline=False)
        collection_url = input(" > ")
        if collection_url.endswith("/"):
            collection_url = collection_url[:-1]
        elif not collection_url:
            rgb("[!] No collection url entered! quitting!", "#ff0000")
            sys.exit()

    if not collection_name:
        rgb("[?] Enter collection name", "#ffff00", newline=False)
        collection_name = input(" > ")
        if not collection_name:
            rgb("[!] No collection name entered! quitting!", "#ff0000")
            sys.exit()
        else:
            db.create_table(collection_name)

    if not number_of_items:
        rgb("[?] Enter number of items you want to pull", "#ffff00", newline=False)
        number_of_items = int(input(" > "))
        if not number_of_items:
            rgb("[!] No number of items entered! quitting!", "#ff0000")
            sys.exit()

    if not skip_fetch:
        rgb("[?] Skip fetching data (y/n)", "#ffff00", newline=False)
        if input(" > ").lower() == "y":
            skip_fetch = True

    time_start = time.time()
    try:
        if not skip_fetch:
            rgb(f"[+] Started pulling data from {collection_name}", "#00ff00")
            rgb(f"[+] Threads: {THREADS} | Amount per Thread {number_of_items // THREADS}", "#00ff00")
            # THIS IS HEAVY AND SLOW,
            # LIKE UR MOM LMAOO
            if not skip_fetch:
                get_collection_data(collection_url, number_of_items, collection_name)
                counter = threading.Thread(target=_t_progress_ticker, args=(number_of_items, time_start))
                counter.start()
                counter.join()

    except KeyboardInterrupt:
        rgb("\n[!] KeyboardInterrupt", "#ff0000")

    except Exception as e:
        rgb(f"\n[!] {e}", "#ff0000")

    finally:
        db.__save__()

        rgb(f"[+] items pulled successfully in {round(time.time() - time_start, 2)} seconds \n"
            f"[-] {Failed} items failed {round(Failed / number_of_items * 100, 2)}% of total",
            color="#00ff00")

        for idx, item in enumerate(db.get_rarest_items(collection_name, 30)):
            db.get_item_stat(collection_name, item[1])


if __name__ == "__main__":
    setup()
    if args["url"] is not None and args["collection_name"] is not None and args["count"] is not None:
        main(args["url"], args["collection_name"], args["count"], args["skip"])
    else:
        main()