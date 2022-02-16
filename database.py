import sqlite3
import threading

from utils import rgb


class Database:
    def create_table_if_not_exists(self, table_name: str):
        """
        DROP IF EXISTS CREATE NEW
        :param table_name:
        :return:
        """
        self._cursor.execute(f"""
        DROP TABLE IF EXISTS {table_name};
        """)

        self._cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} 
        (
            name            TEXT,
            attribute_type  TEXT,
            attribute_value TEXT
        );
        """)

    def add_attributes(self, nft_metadata: dict = None):
        for attr in nft_metadata["attributes"]:
            self._items.append((nft_metadata["name"], attr["trait_type"], attr["value"]))


    def _flush(self, table_name: str):
        rgb(f"[+] Flushing {table_name}", color=0x00ff00)
        with self._t_lock:
            self._cursor.executemany(f"""
            INSERT INTO {table_name} (name, attribute_type, attribute_value)
            VALUES (?, ?, ?)
            """, self._items)
            self._connection.commit()
        rgb(f"[+] Done", color=0x00ff00)


    def get_rarest_items(self, table_name: str, limit: int = 20):
        # either this, or the old method
        with self._t_lock:
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS tmp_{table_name}_appearance;
            """)
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name}_with_nulls;
            """)
            self._cursor.execute(f"""
            CREATE TABLE {table_name}_with_nulls
            AS
            SELECT h.name, ha.attribute_type, hap.attribute_value
            FROM (SELECT distinct(name) FROM {table_name}) as h
            CROSS JOIN (SELECT DISTINCT(attribute_type) FROM {table_name}) as ha
            LEFT JOIN {table_name} hap 
            ON h.name = hap.name AND ha.attribute_type = hap.attribute_type;
            """)
            self._cursor.execute(f"""
            INSERT INTO {table_name} 
            VALUES(NULL, 'Traits count', NULL);
            """)
            self._cursor.execute(f"""
            UPDATE {table_name}_with_nulls
            SET attribute_value = name
            where attribute_value is NULL;
            """)
            self._cursor.execute(f"""
            CREATE TABLE tmp_{table_name}_appearance
            AS
            SELECT attribute_value,
                   count(attribute_value) AS Appereance,
                   count(*) OVER (PARTITION BY NULL) AS Total
            FROM {table_name}_with_nulls AS h
            GROUP BY attribute_value;
            """)
            self._cursor.execute(f"""
            SELECT row_number() 
            OVER (ORDER BY 1/exp(SUM(log((TA.Appereance / CAST(TA.Total AS FLOAT))))) DESC) 
            AS RowNumber, h.name, 1/exp(SUM(log((TA.Appereance / CAST(TA.Total AS FLOAT))))) AS SCORE
            FROM {table_name}_with_nulls as h
            LEFT JOIN tmp_{table_name}_appearance as TA ON h.attribute_value=TA.attribute_value
            GROUP BY h.name
            ORDER BY SCORE DESC
            LIMIT ?;
            """, (limit,))
            data = self._cursor.fetchall()
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS tmp_{table_name}_appearance;
            """)
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name}_with_nulls;
            """)
            return data


    def get_name_stat(self, table_name: str, name: str):
        with self._t_lock:
            self._cursor.execute(f"""
            SELECT attribute_type, attribute_value
            FROM {table_name}
            WHERE name = ?;
            """, (name,))
            data = self._cursor.fetchall()
            return data


    def table_exists(self, table_name: str):
        with self._t_lock:
            self._cursor.execute(f"""
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name=?;
            """, (table_name,))
            data = self._cursor.fetchone()
            if data is None:
                return False
            else:
                return True


    def __init__(self):
        self._connection = sqlite3.connect("nft.db", check_same_thread = False)
        self._cursor = self._connection.cursor()
        self._t_lock = threading.Lock()
        self._items: list[tuple] = []


    def __enter__(self):
        self._t_lock.acquire(True)
        return self._cursor


    def __exit__(self, exc_type, exc_val, exc_tb):
        self._t_lock.release()
        if exc_type:
            rgb(exc_type, "#ff0000")
            rgb(exc_val, "#ff0000")
            rgb(exc_tb, "#ff0000")
        self._connection.commit()


    def __save__(self, table_name: str):
        try:
            self._flush(table_name)
            self._connection.commit()
        except sqlite3.OperationalError:
            pass
        except Exception as e:
            rgb(f"[!] {e}", "#ff0000")


    def __close__(self, table_name: str):
        rgb("\n[*] Database closed", "#00ff00")
        self.__save__(table_name)
        self._connection.close()


database = Database()

if __name__ == "__main__":
    pass
