import asyncio
import aiosqlite

class SQLHandle:
    def __init__(self):
        self.task_list: list[asyncio.Task] = []        

    async def setup(self, profile:str):
        self.conn = await aiosqlite.connect(f"client_data/history/{profile}.db")
        self.cursor = await self.conn.cursor()

    async def exec(self, query:str, args:tuple =(), commit:bool =True):
        if(args):
            await self.cursor.execute(query, args)
        else:
            await self.cursor.execute(query)

        if(commit):
            await self.conn.commit()

    async def write(self, sender_id:str, content:str, timestamp:int, second_id:str = ''):
        
        if(not second_id):
            sql_query = '''INSERT INTO msgHistory (sender_id, content, timestamp)
            VALUES (?,?,?)'''
            await self.exec(sql_query, (sender_id, content, timestamp))
            return
        
        if(second_id.startswith('user_')):      
            sql_query = '''INSERT INTO msgHistory (sender_id, receiver_id, content, timestamp)
            VALUES (?,?,?,?)'''
            await self.exec(sql_query, (sender_id,  content, timestamp))   
            return
        
        if(second_id.startswith('room_')):
            sql_query = '''INSERT INTO msgHistory (sender_id, room_id, content, timestamp)
            VALUES (?,?,?,?)'''
            await self.exec(sql_query, (sender_id, content, timestamp))   
            return
        
sql_db = SQLHandle()