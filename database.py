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


    """
1.) Trait rarity ranking - solely dependent on the most rare trait a piece possesses
2.) Average trait rarity - A simple average of the percentage frequency of all traits associated with a piece
3.) Statistical rarity   - Combining the percentage frequency of all traits by multiplying them together
4.) Rarity score         - Scored by summing up the inverse of the percentage frequency of all traits 
                           (rarity.tools website’s method)
    """
    def get_total_values(self, table_name: str):
        """
        :param table_name:
        :return:
        get total number of values in table
        >>> "hape" -> 73,777
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(*)
            FROM {table_name}
            """)
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def get_attribute_type_frequency(self, table_name: str, attribute_type: str):
        """
        :param table_name:
        :param attribute_type:
        :return:
        get how many times type occurs
        >>> "fur" -> 80
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(attribute_type)
            FROM {table_name}
            WHERE attribute_type = ?
            """, (attribute_type,))
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def get_attribute_value_frequency(self, table_name: str, attribute_type: str, attribute_value: str):
        """
        :param table_name:
        :param attribute_type:
        :param attribute_value:
        :return:
        get how many times value occurs inside an attribute
        >>> "fur", "champagne" -> 2
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(attribute_value)
            FROM {table_name}
            WHERE attribute_type = ? AND attribute_value = ?
            """, (attribute_type, attribute_value))
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def iter_attribute_type(self, table_name: str):
        """
        :param table_name:
        :return:
        iterate through all attribute types
        >>> "fur" -> "fur"
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT DISTINCT attribute_type
            FROM {table_name}
            """)
            data = self._cursor.fetchall()
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            _ = [x[0] for x in data]
            return _


    def iter_attribute_value(self, table_name: str, attribute_type: str):
        """
        :param table_name:
        :param attribute_type:
        :return item name and attribute value:
        iterate through all attribute values and unpack into name and attribute value
        >>> "fur", "champagne" -> "champagne"
        >>> for name, value in iter_attribute_value(table_name, "Fur"):
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT DISTINCT name, attribute_value
            FROM {table_name}
            WHERE attribute_type = ?
            """, (attribute_type,))
            data = self._cursor.fetchall()
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def get_value_amount(self, table_name: str, attribute_type: str, attribute_value: str):
        """
        :param table_name:
        :param attribute_type:
        :param attribute_value:
        :return:
        get rarity of a value
        >>> "fur", "champagne" -> 0.01
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(attribute_value)
            FROM {table_name}
            WHERE attribute_type = ? AND attribute_value = ?
            """, (attribute_type, attribute_value))
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def update_rarity(self, table_name: str, item_name: str, attribute_type: str, attribute_value: str, rarity: float):
        """
        :param table_name:
        :param item_name:
        :param attribute_type:
        :param attribute_value:
        :param rarity:
        :return:
        update rarity of a value
        >>> "fur", "champagne" -> 0.01
        """
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            UPDATE {table_name}
            SET rarity = ?
            WHERE name = ? AND attribute_type = ? AND attribute_value = ?
            """, (rarity, item_name, attribute_type, attribute_value))
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()


    def amount_of_items(self, table_name):
        """
        :param table_name:
        :return:
        get amount of items from a collection table.
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"SELECT COUNT(DISTINCT name) FROM {table_name}")
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


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
    print("start iter")
    progress = 0
    total = database.get_total_values("hape")
    for attribute in database.iter_attribute_type("hape"):
        for name, value in database.iter_attribute_value("hape", attribute):
            rarity = database.get_value_amount('hape', attribute, value) / total
            database.update_rarity("hape", name, attribute, value, rarity)

            # print(f"{name} - {attribute} - {value} - {rarity * 100:.6f}%")
            rgb(f"\r[UPDATE] {progress / total:.4f}%", "#00ff00", newline=False)
            progress += 1
