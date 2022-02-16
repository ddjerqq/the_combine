from utils import *
from database import database as db
from demons import spawn_demons


def main() -> None:
    os.system(f"title \"NFT SNYPER | DDJERQQ\"")

    c_name, c_uri, j_end = prompt()

    if not db.table_exists(c_name):
        db.create_table_if_not_exists(c_name)
        os.system(f"title \"NFT SNYPER | DDJERQQ | {c_name}\"")

        _time_start = time.time()
        rgb(f"[#] Please wait...", color=0xffff00, newline=False)
        number_of_items = binary_find(c_uri, j_end)
        clear()
        spawn_demons(c_uri, c_name, number_of_items, j_end)
        db.__save__(c_name)

    items = db.get_rarest_items(c_name, 20)

    if items:
        pretty_iterable([x[1] for x in items])


if __name__ == "__main__":
    try:
        clear()
        main()
    except KeyboardInterrupt:
        _exit = vinput("\n[?] Enter to exit", lambda x: True)
        sys.exit()
