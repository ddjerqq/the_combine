import sqlite3
import threading

from utils import rgb

"""
{
"name": "HAPE #1",
"description": "8192 next-generation, high-fashion HAPES.",
"image": "https://meta.hapeprime.com/1.png",
"external_url": "https://hapeprime.com",
"attributes": [
    {
        "trait_type": "Fur",
        "value": "Champagne"
    },
    {
        "trait_type": "Head",
        "value": "Pained"
    },
    {
        "trait_type": "Eyes",
        "value": "Peri Tone"
    },
    {
        "trait_type": "Clothing",
        "value": "Essential T-Shirt (Geometric Urban)"
    },
    {
        "trait_type": "Headwear",
        "value": "5 Panel (Red)"
    },
    {
        "trait_type": "Birthday",
        "value": "22/04"
    },
    {
        "trait_type": "Heart Number",
        "value": "020914375592"
    }
]
},
"""

_t_lock = threading.Lock()


class Database:
    def create_table(self, table_name):
        self._cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} 
        (
            name            TEXT NOT NULL,
            attribute_type  TEXT NOT NULL,
            attribute_value TEXT NOT NULL
        );
        """)

    def add_attributes(self, table_name: str, nft_metadata: dict):
        attributes_tuples = []
        for attr in nft_metadata["attributes"]:
            attributes_tuples.append((
                    nft_metadata["name"],
                    attr["trait_type"],
                    attr["value"]
                ))
            # TODO ASK IF THIS IS SLOWER THAN DOING IT IN BULK
        try:
            _t_lock.acquire(True)
            self._cursor.executemany(f"""
            INSERT INTO {table_name} (name, attribute_type, attribute_value)
            VALUES (?, ?, ?);
            """, attributes_tuples)
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()

    # https://meta.hapeprime.com/

    """
    1.) Trait rarity ranking - solely dependent on the most rare trait a piece possesses
    2.) Average trait rarity - A simple average of the percentage frequency of all traits associated with a piece
    3.) Statistical rarity   - Combining the percentage frequency of all traits by multiplying them together
    4.) Rarity score         - Scored by summing up the inverse of the percentage frequency of all traits 
    """

    # TODO IMPLEMENT CONTAINS
    # TODO IMPLEMENT
    def get_rarest_items(self, table_name: str):
        raise NotImplementedError


    def __init__(self):
        self._connection = sqlite3.connect("nft.db", check_same_thread = False)
        self._cursor = self._connection.cursor()

    def __enter__(self):
        _t_lock.acquire(True)
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        _t_lock.release()
        if exc_type:
            rgb(exc_type, "#ff0000")
            rgb(exc_val, "#ff0000")
            rgb(exc_tb, "#ff0000")
        self._connection.commit()

    def __save__(self):
        try:
            self._connection.commit()
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")

    def __close__(self):
        rgb("\n[*] Database closed", "#00ff00")
        self.__save__()
        self._connection.close()


database = Database()
