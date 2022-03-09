import asqlite
import asyncio
import sqlite3


class AsyncDataBase(object):
    def __init__(self):
        self.cursor = None

    @staticmethod
    async def init(loop: asyncio.AbstractEventLoop):
        db = AsyncDataBase()
        db.cursor = await asqlite.connect(":memory:", loop=loop)
        await db.create()
        return db

    async def create(self):
        await self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS test 
        (
            name TEXT, 
            age INTEGER
        )""")

    async def insert(self, name: str, age: int):
        await self.cursor.execute(f"""
        INSERT INTO test (name, age) VALUES (?, ?)
        """, (name, age))

    async def select(self) -> list[sqlite3.Row]:
        res = await self.cursor.execute("SELECT * FROM test")
        return await res.fetchall()


async def main():
    loop = asyncio.get_running_loop()
    db = await AsyncDataBase.init(loop)
    await db.create()
    await db.insert("John", 20)
    await db.insert("Jane", 21)
    await db.insert("Jack", 22)
    await db.insert("Jill", 23)
    res = await db.select()
    for row in res:
        print(row.keys())
        print(tuple(row))


if __name__ == "__main__":
    asyncio.run(main())
