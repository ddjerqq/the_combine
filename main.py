import requests
import threading

# local
from utils import *
from headers import random_useragent
from database import database as db

# constants
_t_lock = threading.Lock()
THREADS = 20  # change this to 4x your threads.
progress = 1
failed = 0


def _t_pull(start: int, amount: int, collection_url: str, collection_name: str):
    global progress, failed
    for i in range(start, start+amount):
        try:
            r = requests.get(
                f"{collection_url}/{i}",
                headers={"user-agent": random_useragent()}
            )
        except ConnectionError:
            continue


        if r.status_code != 200:
            r2 = requests.get(
                f"{collection_url}/{i}",
                headers = {"user-agent": random_useragent()}
            )
            if r2.status_code != 200:
                failed += 1
                progress += 1
                if not failed % 3:
                    db.__save__()
                continue
            else:
                r = r2

        # print(r.json())

        progress += 1
        db.add_attributes(collection_name, r.json())


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
    while True:
        rgb(
            f"\r[+] {progress:<5}/ {total} | failed: {failed} | {round((progress / total) * 100, 2)}%",
            "#00ff00",
            newline=False
        )
        if progress >= total:
            break
    rgb(
        f"\r[+] {total:<5}/ {total} | failed: {failed} | 100.00%",
        "#00ff00",
        newline = False
    )


def setup():
    os.system("clear || cls")
    if not os.path.isdir("data"):
        os.mkdir("data")
    welcome_screen()


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
        rgb(f"\n[+] {db.size_of_table(collection_name)} "
            f"items pulled successfully in {round(time.time() - time_start, 2)} seconds", "#00ff00")
        if failed > 0:
            rgb(f"[-] {failed} items failed {round(failed / number_of_items * 100, 2)}% of total", "#ff0000")

        rarest_attributes = db.rarest_attributes(collection_name)
        for rarest_attributes in rarest_attributes:
            for attr in db.rarest_values_of_attribute(collection_name, rarest_attributes[0]):
                total = db.total_number_of_values(collection_name)
                rgb(f"{attr[0]} has {attr[1]} {attr[2]}/{total}", "#00ff00")
                rgb(f"{round((attr[2] / total) * 100, 4)}%", "#00ff00")


if __name__ == "__main__":
    main()
