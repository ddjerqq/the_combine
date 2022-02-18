import demons
from utils import *
from database import database as db

# TODO aws sites are sending us json in r.content and giving 403


def main() -> None:
    os.system(f"title \"NFT SNYPER | DDJERQQ\"")

    c_name, c_uri, j_end = prompt()

    db.create_table(c_name)

    os.system(f"title \"NFT SNYPER | DDJERQQ | {c_name}\"")

    number_of_items = super_find(c_uri, j_end)

    clear()

    demons.spawn_demons(c_uri, c_name, number_of_items, j_end)

    rgb(f"\n[+] Done\n", color=0x00ff00, newline=False)

    rarest_items = [item[1] for item in db.get_rarest_items(20)]

    if rarest_items:
        pretty_iterable(rarest_items)

    download = vinput(
        "\n[y/n] Download rarest items?",
        lambda x: x.lower() in ["y", "yes", "n", "no"]
    )
    download = True if download in ["y", "yes"] else False

    if download:
        demons.TPuller.downloader(*rarest_items, collection_name=c_name)


# QmUTFezR7ubZipbTr6HmSM9CVHmXYhXqAsiKQMaC3CG3o4
# QmT1b952aadWCSLCEDdRLS2L3E2asi9U7nAK89RJE98KkS

if __name__ == "__main__":
    try:
        clear()
        main()
    except KeyboardInterrupt:
        _exit = vinput("\n[?] Enter to exit", lambda x: True)
        sys.exit()
    finally:
        db.__close__()
