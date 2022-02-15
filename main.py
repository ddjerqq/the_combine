# local
from utils import *
from database import database as db
from demons import spawn_demons

Progress = 1
Failed = 0
Done = False


proxy = {"https": "http://metacircuits:dZwUllzyyZWL41U0@p.litespeed.cc:31112"}


def main() -> None:
    c_name, skip, c_uri = prompt()
    db.create_table(c_name)
    os.system(f"title NFT SNYPER | DDJERQQ | {c_name}")
    if not skip:
        clear()
        _time_start = time.time()
        number_of_items = binary_find(c_uri)
        spawn_demons(c_uri, c_name, number_of_items)

    for idx, item in enumerate(db.get_rarest_items(c_name, 20)):
        rgb(f"#{idx:<3} {item[1]}", color=0x00ff00)


if __name__ == "__main__":
    clear()
    main()
