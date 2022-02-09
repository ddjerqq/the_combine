import sqlite3
import os
import time
import json
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
            attributes_tuples.append(
                (
                    nft_metadata["name"],
                    attr["trait_type"],
                    attr["value"]
                )
            )

        try:
            _t_lock.acquire(True)
            self._cursor.executemany(f"""
            INSERT INTO {table_name} (name, attribute_type, attribute_value)
            VALUES (?, ?, ?)
            """, attributes_tuples)
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()

    def rarest_attributes(self, table_name: str):
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT attribute_type, COUNT(attribute_type) AS count
            FROM {table_name}
            GROUP BY attribute_type
            ORDER BY count
            LIMIT 10
            """)
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return self._cursor.fetchall()

    def rarest_values_of_attribute(self, table_name: str, attribute_type: str):
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT name, attribute_value, COUNT(attribute_value) AS count
            FROM {table_name}
            WHERE attribute_type = ?
            GROUP BY attribute_value
            ORDER BY count
            LIMIT 10
            """, (attribute_type,))
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return self._cursor.fetchall()

    def number_of_values(self, table_name: str, attribute_value: str):
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(name)
            FROM {table_name}
            WHERE attribute_value = ?
            """, (attribute_value,))
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return self._cursor.fetchone()[0]

    def total_number_of_values(self, table_name: str):
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(name)
            FROM {table_name}
            """)
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return self._cursor.fetchone()[0]

    def size_of_table(self, table_name):
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"SELECT COUNT(DISTINCT name) FROM {table_name}")
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return self._cursor.fetchone()[0]

    def __init__(self):
        self._connection = sqlite3.connect("nft.db", check_same_thread=False)
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


if __name__ == "__main__":
    pass
