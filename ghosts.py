import time
import asyncio
import aiohttp
from headers import random_useragent
from models.metadata import Metadata
from rgbprint.new_print import _print as print
from rgbprint.colors import Colors


PROXY = "http://metacircuits:dZwUllzyyZWL41U0@p.litespeed.cc:31112"
IPFS_URI = "http://ipfs.io/ipfs/{}/{}"
HEADER = lambda: {"accept": "application/json", "user-agent": random_useragent()}


async def _ghost(
        session: aiohttp.ClientSession,
        uri: str,
        item_index: int,
        progress_tracker: list[int]) -> Metadata | None:
    """
    a basic ghost model

    :param session: aiohttp.ClientSession object
    :param uri: the url of the collection. should support .format() with the item index
    :param item_index: the item which you want to pull
    :param progress_tracker: the array, passed by referrence, which will store the progress
    :return: Metadata object made from the json response or None if item could not be found
    """

    busted = False
    while True:
        try:
            r = await session.get(
                uri.format(item_index),
                headers=[None, HEADER()][busted],
                proxy=[None, PROXY][busted]
            )
            d = await r.json()
        except Exception:
            # TODO tweak this to perfection
            # TODO catch 404s or offlimits
            await asyncio.sleep(0.25)
            busted = True
        else:
            break

    metadata = Metadata.from_json(d)

    progress_tracker[0] += 1

    if not item_index % 5:
        print(f"\r[+] progress [{progress_tracker[0]:05}]",
              end="", flush=True, color=Colors.GREEN)

    # TODO
    # riti gansxvavdeba thc-hydra sgan
    # aris tu ara medusa async?

    return metadata



def summon(uri_or_hash: str, _max: int, col_name: str, *, loop: asyncio.BaseEventLoop | None = None):
    running_loop = loop or asyncio.get_event_loop()
    summon_start = time.time()
    session = aiohttp.ClientSession()

    if "Qm" in uri_or_hash.split("/"):
        ...

    uri = ...

    progress = [0]
    ghosts = [_ghost(session, uri, item, progress) for item in range(_max)]
    ghost_group = asyncio.gather(*ghosts)

    data = running_loop.run_until_complete(ghost_group)

    print(f"\n[+] pulling {len(data)} items took {(time.time() - summon_start):.4f} seconds", color=Colors.GREEN)


    # start saving


    # todo check hash
    ...





