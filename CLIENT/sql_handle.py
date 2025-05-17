import asyncio
import aiosqlite

class SQLHandle:
    '''Class Handling all things related to DB Management'''

    def __init__(self):
        pass
    
    async def setup(self, profile:str):
        '''Connect to the Proper DB for user msgHistory'''

        self.conn = await aiosqlite.connect(f"client_data/history/{profile}.db")
        self.cursor = await self.conn.cursor()

    async def exec(self, query:str, args:tuple =(), commit:bool =True):
        '''Execute any SQL Query with Given Args; Commiting is Optional'''

        if(args):
            await self.cursor.execute(query, args)
        else:
            await self.cursor.execute(query)

        if(commit):
            await self.conn.commit()

    async def write(self, sender_id:str, content:str, timestamp:int, second_id:str = ''):
        '''Write Onto the msgHistory table with given value'''
        
        # Received Direct Message
        if(not second_id):
            sql_query = '''INSERT INTO msgHistory (sender_id, content, timestamp)
            VALUES (?,?,?)'''
            await self.exec(sql_query, (sender_id, content, timestamp))
            return
        
        # Sent Direct Message 
        if(second_id.startswith('user_')):      
            sql_query = '''INSERT INTO msgHistory (sender_id, receiver_id, content, timestamp)
            VALUES (?,?,?,?)'''
            await self.exec(sql_query, (sender_id, second_id, content, timestamp))   
            return
                
        # Received/Sent Room Message
        if(second_id.startswith('room_')):
            sql_query = '''INSERT INTO msgHistory (sender_id, room_id, content, timestamp)
            VALUES (?,?,?,?)'''
            await self.exec(sql_query, (sender_id, second_id, content, timestamp))   
            return

#__MAIN__   
sql_db = SQLHandle()