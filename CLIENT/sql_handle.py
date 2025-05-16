import asyncio
import aiosqlite

class SQLHandle:
    def __init__(self):
        self.task_list: list[asyncio.Task] = []
        self.return_data = None

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

        # self.return_data = await self.cursor.fetchall()
        # return self.return_data
    
    async def cleanup(self):
        for task in self.task_list:
            task.cancel()
            try: await task
            except asyncio.exceptions.CancelledError: pass

        return
    

    def call_cleanup(self):
        task = asyncio.create_task(self.cleanup())
        self.task_list.append(task)

    def call_write(self, query:str, args:tuple =()):
        task = asyncio.create_task(self.write(query, args))
        self.task_list.append(task)


sql_db = SQLHandle()