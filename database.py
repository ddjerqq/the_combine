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
                           (rarity.tools website’s method)
    """

    def get_total_names(self, table_name: str):
        """
        :param table_name:
        :return:
        get total number of pieces in table
        >>> "hape" -> 9,346
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(DISTINCT name)
            FROM {table_name}
            """)
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def get_distinct_values(self, table_name: str):
        """
        :param table_name:
        :return:
        get total number of distinct different values in table
        >>> "hape" -> 9000 # "or something"
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(DISTINCT attribute_value)
            FROM {table_name}
            """)
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def get_total_values(self, table_name: str):
        """
        :param table_name:
        :return:
        get total number of values in table
        >>> "hape" -> 80000 # "or something"
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(attribute_value)
            FROM {table_name}
            """)
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def get_total_attributes(self, table_name: str):
        """
        :param table_name:
        :return:
        get total number of attributes in table
        >>> "hape" -> 16 # "or something"
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT COUNT(DISTINCT attribute_type)
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


    def get_traits_of_name(self, table_name: str, name: str):
        """
        :param table_name:
        :param name: name of the monkey
        :return: name type value
        get all traits of a name
        >>> "hape" -> ["fur", "champagne"]
        """
        data = None
        try:
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT name, attribute_type, attribute_value
            FROM {table_name}
            WHERE name = ?
            GROUP BY attribute_type, attribute_value;
            """, (name,))
            data = self._cursor.fetchall()
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data


    def _get_value_rarity(self, table_name: str, attribute_value: str):
        """
        :param table_name:
        :param attribute_value:
        :return:
        get rarity of a value
        >>> "champagne" -> "rare"
        """
        data = None
        try:
            total = self.get_total_values(table_name)
            _t_lock.acquire(True)
            self._cursor.execute(f"""
            SELECT (((COUNT(attribute_value) + 0.0 ) / ?) * 100) as rarity 
            FROM {table_name}
            WHERE attribute_value = ?
            """, (total, attribute_value))
            data = self._cursor.fetchone()[0]
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data

    # RULE 1
    def get_rarest_trait_of_name(self, table_name: str, name: str):
        """
        :param table_name:
        :param name: name of the monkey
        :return: type value
        get the rarest trait of a name
        >>> "hape" -> ["fur", "champagne"]
        """
        data = None
        try:
            _t_lock.acquire(True)
            for rarity in self._get_value_rarity(table_name, name):
                self._cursor.execute(f"""
                SELECT attribute_type, attribute_value
                FROM {table_name}
                WHERE name = ? AND rarity = ?
                """, (name, rarity))
                data = self._cursor.fetchone()
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")
        finally:
            _t_lock.release()
            return data

    # RULE 2
    def get_average_trait_rarity_of_name(self, table_name: str, name: str):
        avg = []
        for _name, _attr_type, _val in self.get_traits_of_name(table_name, name):
            appearance_of_val = self.get_attribute_value_frequency(table_name, _attr_type, _val)
            rarity = (appearance_of_val / self.get_total_values(table_name)) * 100
            # print(_val, "has", rarity, "% rarity")
            # DEBUG ^
            avg.append(rarity)
        return sum(avg) / len(avg)


    def get_table_stat(self, table_name: str):
        """
        Get the stats of a table, print: \n
        total pieces
        total values
        different values
        different types
        :param table_name:
        :return: name type value
        get all traits of a name
        >>> "hape #3" -> ["fur", "champagne"]
        """
        rgb(f"[+] total pieces - {self.get_total_names(table_name)}              \n"
            f"[+] total values - {self.get_total_values(table_name)}             \n"
            f"[+] distinct values - {self.get_distinct_values(table_name)}       \n"
            f"[+] distinct attributes - {self.get_total_attributes(table_name)}  \n",
            color="#00ff00")


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

if __name__ == "__main__":
    print("HAPE #4280 ")
    print("rarest trait", database.get_rarest_trait_of_name("hape", "HAPE #4280"))
    print("average trait rarity", database.get_average_trait_rarity_of_name("hape", "HAPE #4280"), "%")
