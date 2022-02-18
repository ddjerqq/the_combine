import os
import sys
import time
import random
import threading
from typing import Iterable


import requests
from headers import random_useragent

LOGO = """
███████╗ ███╗   ██╗ ██╗   ██╗ ██████╗  ███████╗ ██████╗ 
██╔════╝ ████╗  ██║ ╚██╗ ██╔╝ ██╔══██╗ ██╔════╝ ██╔══██╗
███████╗ ██╔██╗ ██║  ╚████╔╝  ██████╔╝ █████╗   ██████╔╝
╚════██║ ██║╚██╗██║   ╚██╔╝   ██╔═══╝  ██╔══╝   ██╔══██╗
███████║ ██║ ╚████║    ██║    ██║      ███████╗ ██║  ██║
╚══════╝ ╚═╝  ╚═══╝    ╚═╝    ╚═╝      ╚══════╝ ╚═╝  ╚═╝"""

PROXY = {"http": "http://metacircuits:dZwUllzyyZWL41U0@p.litespeed.cc:31112"}


def clear():
    os.system("clear || cls")
    welcome_screen()


def welcome_screen() -> None:
    for char in LOGO:
        if char == "█":
            rgb(
                char,
                color=(random.randint(200, 255), random.randint(25, 75), random.randint(30, 50)),
                newline=False
            )
        else:
            rgb(char, newline=False)
    print()


def rgb(text: str, /, color: str | tuple | int = "#ffffff", *, newline: bool = True) -> None:
    """
        print rgb color 🎊 with this
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        \n
        ~~~~~~~~~~~~~~
        Args:
            text  (str): the text you want to print, str() method is automatically called on it
            color (str): #000000 hex representation of color, prefixed with # or not
            color (tuple): (red, green, blue) color tuple
            color (int): 0xff0000 integer representation of hex color.
            newline (bool default False): whether or now you want to print a new line \n
            after you are done printing rgb, you can insert colored text if you set this to false
        \n
        ~~~~~~~~~~~~~~
        Retrurns:
            None
        \n
        ~~~~~~~~~~~~~~
        Example:
            >>> rgb("lorem ipsum", "#ff0000")
            >>> rgb("lorem ipsum", (255, 0, 0))
            >>> rgb("lorem ipsum", 0xff0000)
            >>> rgb("lorem", "#ff0000", newline=False)
            >>> rgb("ipsum", "#00ff00", newline=False)
    """
    if type(color) == str:
        color = tuple(int(color.lstrip("#")[i: i + 2], 16) for i in (0, 2, 4))

    elif type(color) == tuple:
        pass

    elif type(color) == int:
        blue = color % 256
        green = ((color - blue) // 256) % 256
        red = ((color - blue) // 256 ** 2) - green // 256
        color = red, green, blue

    else:
        raise Exception(f"invalid color {color}")

    if sum(color) > 765:
        raise Exception(f"invalid color {color}")

    end = "\n" if newline else ""
    _color = f"\033[38;2;{color[0]};{color[1]};{color[2]}m"
    _end_char = "\033[0m"

    sys.stdout.write(_color + str(text) + _end_char + end)
    sys.stdout.flush()


def vinput(question: str, validator: callable) -> str:
    """
    validates user input with this
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    example input: \n
    >>> vinput("Collection uri", lambda x: x.startswith("ipfs://") or x.startswith("https://"))

    :param question: str, text to ask the user, this will be printed [?] yellow
    :param validator: function which will validate the user input (should return bool)
    :return: str, validated input
    """
    while True:
        rgb(f"\r{question}", color="#ffff00", newline=False)
        ans = input(" > ").strip()
        if validator(ans):
            break
        else:
            rgb("[!] invalid input", color="#ff0000", newline=False)
            time.sleep(0.5)
    return ans


def _t_check_item(uri: str, item_idx: int, idx: int, itemplace: list, json_at_the_end: bool):
    proxy_needed = False
    while 1:
        try:
            item_idx = 1 if not item_idx else item_idx
            r = requests.get(
                f"{uri}/{item_idx}.json" if json_at_the_end else f"{uri}/{item_idx}",
                proxies=PROXY if proxy_needed else None,
                headers={"user-agent": random_useragent()}
            )
            match r.status_code:
                case 200:
                    itemplace[idx] = 1
                    break
                case 404:
                    itemplace[idx] = 0
                    break
                case _:
                    proxy_needed = True
                    continue
        except requests.exceptions.ProxyError or ConnectionError:
            pass


def super_find(uri: str, json_at_the_end: bool) -> int:
    """
    get number of items in a collection using magic threads
    :param uri: please pass the uri ready for fetching
    :param json_at_the_end: bool, if the collection URI ends with json
    :return:
    """
    low = 0

    # get thousands
    thousands = [0 for _ in range(10)]
    thousands_threads = []
    for i in range(10):
        t = threading.Thread(target=_t_check_item, args=(uri, i*1000, i, thousands, json_at_the_end))
        t.start()
        thousands_threads.append(t)
    for t in thousands_threads:
        t.join()

    for idx, thousand in enumerate(thousands):
        if thousand:
            continue
        else:
            low = (idx - 1) * 1000
            break

    # get hundreds
    hundreds = [0 for _ in range(10)]
    hundreds_threads = []
    for i in range(10):
        t = threading.Thread(target=_t_check_item, args=(uri, low + i*100, i, hundreds, json_at_the_end))
        t.start()
        hundreds_threads.append(t)
    for t in hundreds_threads:
        t.join()

    for idx, hundred in enumerate(hundreds):
        if hundred:
            continue
        else:
            low += (idx - 1) * 100
            break

    # get tens
    tens = [0 for _ in range(10)]
    tens_threads = []
    for i in range(10):
        t = threading.Thread(target = _t_check_item, args = (uri, low + i * 10, i, tens, json_at_the_end))
        t.start()
        tens_threads.append(t)
    for t in tens_threads:
        t.join()

    for idx, ten in enumerate(tens):
        if ten:
            continue
        else:
            low += (idx - 1) * 10
            break

    # get ones
    ones = [0 for _ in range(10)]
    ones_threads = []
    for i in range(10):
        t = threading.Thread(target = _t_check_item, args = (uri, low + i, i, ones, json_at_the_end))
        t.start()
        ones_threads.append(t)
    for t in ones_threads:
        t.join()

    for idx, one in enumerate(ones):
        if one:
            continue
        else:
            low += idx - 1
            break

    return low


def prompt() -> tuple[str, str, bool]:
    """
    :return: collection_name, collection_url, json_at_the_end
    """
    collection_name = vinput(
        "[str] Enter collection name (only numbers and letters)",
        lambda x: x and all(c.isalpha() or c.isdigit() or c == " " for c in x)
    )
    collection_name = collection_name.replace(" ", "_")

    collection_url = vinput(
        "[str] Token hash (Qm...) OR http/s url without .json or / at the end",
        lambda x:
        ((x.startswith("Qm") and len(x) == 46) and x[-1].isalpha())
        or
        (x.startswith("http"))
    )
    if collection_url.startswith("Qm"):
        collection_url = "https://ipfs.io/ipfs/" + collection_url
    elif "ipfs" in collection_url:
        collection_url = "https://ipfs.io/ipfs/" + collection_url.split("/")[-1]
    else:
        collection_url = collection_url if not collection_url.endswith("/") else collection_url[:-1]


    json_at_the_end = vinput(
        "[y/n] Use .json for metadata",
        lambda x: x.lower() in ["y", "yes", "n", "no"]
    )
    json_at_the_end = json_at_the_end.lower() in ["y", "yes"]

    return collection_name, collection_url, json_at_the_end


def pretty_iterable(iterable: Iterable) -> None:
    iterable = [str(i) for i in iterable]
    max_size = min(len(max(iterable, key=len)), 50)

    g = 0x00ff00
    rgb(f"╔═══════╦═{'═' * max_size}═╗", color = g)

    for idx, item in enumerate(iterable):
        r = (random.randint(200, 255), random.randint(25, 75), random.randint(30, 50))
        rgb(f"║ ", color=g, newline=False)
        rgb(f"#{idx+1:<4}", color=r, newline=False)
        rgb(f" ║ ", color=g, newline=False)
        rgb(f"{''.join(item[0:50]):<{max_size}}", color=r, newline=False)
        rgb(f" ║ ", color=g)

    rgb(f"╚═══════╩═{'═' * max_size}═╝", color = g)


if __name__ == "__main__":
    timestart = time.time()
    i = super_find("https://ipfs.io/ipfs/QmUTFezR7ubZipbTr6HmSM9CVHmXYhXqAsiKQMaC3CG3o4", False)
    print(time.time() - timestart)
    print(i)
