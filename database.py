import sqlite3
import os
import time
import json

from utils import rgb


class Database:
    def create_collection_table(self, collection_name):
        # TODO make new tables, from name
        raise NotImplementedError

    def __init__(self):
        self._connection = sqlite3.connect("nft.db")
        self._cursor = self._connection.cursor()

    def __enter__(self):
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        rgb(exc_type, "#ff0000")
        rgb(exc_val, "#ff0000")
        rgb(exc_tb, "#ff0000")
        self._connection.commit()
