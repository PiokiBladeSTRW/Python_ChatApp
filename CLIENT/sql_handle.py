import asyncio
import aiosqlite

class SQLHandle:
    def __init__(self):
        self.task_list: list[asyncio.Task] = []        

    async def setup(self, profile:str):
        self.conn = await aiosqlite.connect(f"client_data/history/{profile}.db")
        self.cursor = await self.conn.cursor()

    async def write(self, query:str, args:tuple =()):
        if(args):
            await self.cursor.execute(query, args)
        else:
            await self.cursor.execute(query)

        await self.conn.commit()

    async def read(self, query:str, args:tuple =()):
        if(args):
            await self.cursor.execute(query, args)
        else:
            await self.cursor.execute(query)

        return await self.cursor.fetchall()
        
sql_db = SQLHandle()