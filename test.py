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

PROVIDERS = ["ipfs.io", "gateway.ipfs.io"]
URI  = "http://{}/ipfs/{}/{}"
COL_NAME = ""
# TOTAL =
METADATAS = []
HEADER = lambda: {"accept": "application/json", "user-agent": random_useragent()}

MAX = 5049
TASKS = 128


async def _async_hyper_demon(start: int, amount: int) -> None:
    async with aiohttp.ClientSession() as sesh:
        for idx in range(start, amount):
            proxy_needed = False
            while True:
                uri = URI.format(random.choice(PROVIDERS), HASH, idx)
                try:
                    r = await sesh.get(
                        uri,
                        headers=HEADER(),
                        proxy=[None, PROXY][proxy_needed]
                    )
                    data = await r.json()
                except Exception as e:
                    await asyncio.sleep(0.15)
                    proxy_needed = True
                else:
                    break

            metadata = Metadata.from_json(data)
            METADATAS.append(metadata)

            print(f"\rprogress [{len(METADATAS):05}]", end="", flush=True, color=Colors.GREEN)



async def main():
    start = time.time()

    hyper_demons = []

    amount = MAX // TASKS

    for i in range(TASKS):
        hd = asyncio.create_task(_async_hyper_demon(i * amount, (i * amount) + amount))
        hyper_demons.append(hd)

    for hd in hyper_demons:
        await hd

    print(f"\npulling {len(METADATAS)} took {(time.time() - start):.3f} with {TASKS} tasks")
    # print(*METADATAS, sep="\n")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

