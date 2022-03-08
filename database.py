import sqlite3
from utils import *


class Database(object):
    def create_table(self, table_name):
        self._table_name = table_name
        with self._t_lock:
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name};
            """)
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name}_images;
            """)
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS {table_name}_with_nulls;
            """)
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS tmp_{table_name}_appearance;
            """)

            self._cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} 
            (
                name            TEXT,
                attribute_type  TEXT,
                attribute_value TEXT
            );
            """)

            self._cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}_images 
            (
                name       TEXT,
                image_url  TEXT,
                image      BLOB DEFAULT NULL
            );
            """)

    def add_attributes(self, nft_metadata: dict):
        # validate keys
        key_image = "image"
        key_name = "name"
        key_type = "trait_type"
        key_value = "value"
        for k, v in nft_metadata.items():
            if "image" in k:
                key_image = k
            if "name" in k:
                key_name = k
            if "type" in k:
                key_type = k
            if "value" in k:
                key_value = k

        with self._t_lock:
            for attr in nft_metadata["attributes"]:
                if "value" not in attr:
                    attr[key_value] = attr[key_type]

                self._cursor.execute(f"""
                INSERT INTO {self._table_name} (name, attribute_type, attribute_value)
                VALUES (?, ?, ?);
                """, (nft_metadata[key_name], attr[key_type], attr[key_value]))

            self._cursor.execute(f"""
            INSERT INTO {self._table_name}_images (name, image_url)
            VALUES (?, ?);
            """, (nft_metadata[key_name], nft_metadata[key_image]))

    def get_rarest_items(self, limit: int = 20):
        # either this, or the old method
        with self._t_lock:
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS tmp_{self._table_name}_appearance;
            """)
            self._cursor.execute(f"""
            DROP TABLE IF EXISTS {self._table_name}_with_nulls;
            """)
            self._cursor.execute(f"""
            CREATE TABLE {self._table_name}_with_nulls
            AS
            SELECT h.name, ha.attribute_type, hap.attribute_value
            FROM (SELECT distinct(name) FROM {self._table_name}) as h
            CROSS JOIN (SELECT DISTINCT(attribute_type) FROM {self._table_name}) as ha
            LEFT JOIN {self._table_name} hap 
            ON h.name = hap.name AND ha.attribute_type = hap.attribute_type;
            """)
            self._cursor.execute(f"""
            INSERT INTO {self._table_name} 
            VALUES(NULL, 'Traits count', NULL);
            """)
            self._cursor.execute(f"""
            UPDATE {self._table_name}_with_nulls
            SET attribute_value = name
            where attribute_value is NULL;
            """)
            self._cursor.execute(f"""
            CREATE TABLE tmp_{self._table_name}_appearance
            AS
            SELECT attribute_value,
                   count(attribute_value) AS Appereance,
                   count(*) OVER (PARTITION BY NULL) AS Total
            FROM {self._table_name}_with_nulls AS h
            GROUP BY attribute_value;
            """)
            self._cursor.execute(f"""
            SELECT row_number() 
            OVER (ORDER BY 1/exp(SUM(log((TA.Appereance / CAST(TA.Total AS FLOAT))))) DESC) 
            AS RowNumber, h.name, 1/exp(SUM(log((TA.Appereance / CAST(TA.Total AS FLOAT))))) AS SCORE
            FROM {self._table_name}_with_nulls as h
            LEFT JOIN tmp_{self._table_name}_appearance as TA ON h.attribute_value=TA.attribute_value
            GROUP BY h.name
            ORDER BY SCORE DESC
            LIMIT ?;
            """, (limit,))
            data = self._cursor.fetchall()
            return data

    def get_name_stat(self, name: str):
        with self._t_lock:
            self._cursor.execute(f"""
            SELECT attribute_type, attribute_value
            FROM {self._table_name}
            WHERE name = ?;
            """, (name,))
            data = self._cursor.fetchall()
            return data

    def get_image_url(self, name: str):
        with self._t_lock:
            self._cursor.execute(f"""
            SELECT image_url
            FROM {self._table_name}_images
            WHERE name= ?;
            """, (name,))
            data = self._cursor.fetchall()[0][0]
            return data

    def get_value_rarity(self, value: str):
        with self._t_lock:
            self._cursor.execute(f"""
            SELECT COUNT(*)
            FROM {self._table_name}
            WHERE attribute_value = ?;
            """, (value,))
            data = self._cursor.fetchone()
            return data[0]

    def get_item_stat(self, item_name: str, short: bool = False) -> None:
        g = "#00ff00"
        orange = "#ffa500"
        item_data = self.get_name_stat(item_name)
        rgb("╔═══════════════════════════════════════════════════════════════════╗",
            color=g)
        rgb(f"║", color=g, newline=False)
        rgb(f" {item_name:^66}", color=orange, newline=False)
        rgb(f"║", color=g)
        if short:
            rgb("╚═══════════════════════════════════════════════════════════════════╝",
                color = g)
            return

        rgb("╠═══════════════╦═════════════════════════════════════════╦═════════╣",
            color=g)
        rgb(f"║", color=g, newline=False)
        rgb(f" {'Attribute':<14}", color=orange, newline=False)
        rgb(f"║", color=g, newline=False)
        rgb(f" {'Value':<40}", color=orange, newline=False)
        rgb(f"║", color=g, newline=False)
        rgb(f" {'Rarity':<8}", color=orange, newline=False)
        rgb(f"║", color=g)
        rgb("╠═══════════════╬═════════════════════════════════════════╬═════════╣",
            color=g)
        for attr in item_data:
            attr_rarity = 1 / self.get_value_rarity(attr[1]) * 100
            rgb(f"║", color=g, newline=False)
            rgb(f" {attr[0]:<14}", color=orange, newline=False)
            rgb(f"║", color=g, newline=False)
            rgb(f" {attr[1]:<40}", color=orange, newline=False)
            rgb(f"║", color=g, newline=False)
            rgb(f" {str(round(attr_rarity, 4)) + '%' :<8}", color=orange, newline=False)
            rgb(f"║", color=g)
        rgb("╚═══════════════╩═════════════════════════════════════════╩═════════╝",
            color = g)

    def __init__(self):
        self._connection = sqlite3.connect(
            ABSOLUTE_PATH + "\\nft.db",
            check_same_thread=False
        )
        self._cursor = self._connection.cursor()
        self._t_lock = threading.Lock()
        self._items: list[tuple[str, str, str]] = []
        self._table_name = None

        if not os.path.exists(ABSOLUTE_PATH + "\\images\\"):
            os.makedirs(ABSOLUTE_PATH + "\\images\\")

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

    def __save__(self):
        with self._t_lock:
            self._connection.commit()

    def __close__(self):
        with self._t_lock:
            self._connection.close()


database = Database()

if __name__ == "__main__":
    for item in database.get_rarest_items(limit=3):
        database.get_item_stat(item[1])
