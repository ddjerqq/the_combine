import time
import random
import asyncio
import aiohttp
from headers import random_useragent
from models.metadata import Metadata
from rgbprint.new_print import _print as print
from rgbprint.colors import Colors

JSON = False
HASH = "QmTB5PbqdjbQUnbbicjowL82oDvBUBVgR7gLddqxm6th3G"
PROXY = "http://metacircuits:dZwUllzyyZWL41U0@p.litespeed.cc:31112"
# PROVIDERS = ["ipfs.io", "gateway.ipfs.io"]
PROVIDER = "ipfs.io"

URI  = "http://{}/ipfs/{}/{}"
IPURI = "http://httpbin.org/ip"
COL_NAME = ""
HEADER = lambda: {"accept": "application/json", "user-agent": random_useragent()}


METADATAS = []
MAX = 5049


async def _async_hyper_demon(session: aiohttp.ClientSession, start_time: float | int, item: int) -> None:
    proxy_needed = False
    while True:
        uri = URI.format(PROVIDER, HASH, item)
        try:
            r = await session.get(
                uri,
                headers=HEADER(),
                proxy=PROXY if proxy_needed else None
            )
            data = await r.json()
        except Exception:
            await asyncio.sleep(0.5)
            proxy_needed = True
        else:
            break

    metadata = Metadata.from_json(data)
    METADATAS.append(metadata)

    # progress print
    if not item % 3:
        total = len(METADATAS)
        t = int((time.time() - start_time) * 1_000)
        print(f"\rprogress [{total:05}] total: [{t:06}] milliseconds",
              end = "", flush = True, color = Colors.GREEN)


def main():
    running_loop = asyncio.get_event_loop()

    total_start = time.time()
    session = aiohttp.ClientSession()

    hyper_demon_group = asyncio.gather(*[_async_hyper_demon(session, total_start, item) for item in range(MAX)])

    running_loop.run_until_complete(hyper_demon_group)

    print(f"\npulling {len(METADATAS)} items took {(time.time() - total_start):.4f} seconds")

    running_loop.run_until_complete(session.close())

    # feature save data here
    # feature OR save it dynamically, but that will slow us down


if __name__ == "__main__":
    uri = "QmTB5PbqdjbQUnbbicjowL82oDvBUBVgR7gLddqxm6th3G"
    uri = "https://meta.hape.com/"

    if uri.startswith("Qm") and len(uri) == 46:
        uri = f"http://ipfs.io/ipfs/{uri}/{{}}"

    elif "/" in uri and "Qm" in uri:
        for part in uri.split("/"):
            if part.startswith("Qm"):
                uri = part
        uri = f"http://ipfs.io/ipfs/{uri}/{{}}"

    else:
        # test
        if uri[-1].isdigit():
            digilast = uri.split("/")[-1]
            uri = uri.replace(digilast, "")
        uri = uri.replace("https", "http")
        uri += "{}"


    print(uri)



















