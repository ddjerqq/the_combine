from utils import *
from database import database as db
from demons import spawn_demons


def main() -> None:
    os.system(f"title \"NFT SNYPER | DDJERQQ\"")

    c_name, c_uri, j_end = prompt()

    db.create_table(c_name)

    os.system(f"title \"NFT SNYPER | DDJERQQ | {c_name}\"")

    rgb(f"[#] Please wait...", color=0xffff00, newline=False)
    number_of_items = binary_find(c_uri, j_end)
    clear()
    spawn_demons(c_uri, c_name, number_of_items, j_end)
    rgb(f"\n[+] Done\n", color=0x00ff00, newline=False)

    items = db.get_rarest_items(20)

    if items:
        pretty_iterable([i[1] for i in items])


if __name__ == "__main__":
    try:
        clear()
        main()
    except KeyboardInterrupt:
        _exit = vinput("\n[?] Enter to exit", lambda x: True)
        sys.exit()
    finally:
        db.__save__()
