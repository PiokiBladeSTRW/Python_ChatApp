# Header
import json
import time
import asyncio
import websockets

import interface.routing as interface
from sql_handle import sql_db
from session_state import state

class ChatClient: 
    '''
    The Client Object
    Purpose: The primary handler of the Client's Sockets Activity
    Acitivities:
        Connecting to Server
        Sending Messages (not Input)
        Receiving Messages
        Sending Heartbeats
        Updating Files                
    '''   

    def __init__(self):       
        self.heartbeatPing = 20
        self.fileIOFrequency = 30
        self.serverAddress = "ws://localhost:8765"     
        self.exit_code = None               
        
    async def connectClient(self) -> None: 
        # Connect to the Socket Server
        self.clientSock = await websockets.connect(self.serverAddress)

        await self.clientSock.send(json.dumps(
                {"command": state.client_codes['user_join'],"content": state.clientUUID, "type":state.msgTypes['system']}
            ))    
        state.log(f"CONNECTED TO SERVER AT: {self.serverAddress}")     

        asyncio.create_task(self.fileHandle())        
        print("\nConnected to Server! ")        

    '''------------------------------------------------'''

    async def receive(self) -> None:
        state.log(f"Receive Up & Running")
        try:
            async for dataReceived in self.clientSock:
                response = json.loads(dataReceived)
                state.log(f"Received from Server: {response} \n")                
                
                task = await interface.parse_response(response) 
                if(task=='kick'):                     
                    self.exit_code= 0
                
                print()

        except websockets.ConnectionClosedError: 
            state.log(f"Server Closed")
            self.exit_code = 1
            return 

    async def sendPayload(self, payload: tuple) -> None:
        '''Payload : ( Message, Type ) or ( (Command, Arguments), 'sys)'''
        try: 
            state.log(f"Sending Payload: {payload} \n")

            timestamp = time.time()                    
            await self.clientSock.send(state.encode(payload, timestamp))

            # Write to SQL DB
            if(payload[1] == 'msg'):
                await sql_db.write(state.clientUUID, payload[0], timestamp, state.receiver_id)

        except websockets.ConnectionClosedError:
            state.log(f"Server Closed")
            self.exit_code = 1
            return    
   

    '''------------------------------------------------'''

         
    async def heartbeat(self) -> None:
        state.log(f"Heartbeat Up & Running")
        while True:            
            await self.sendPayload( ('', state.msgTypes['heartbeat']) )
            await asyncio.sleep(self.heartbeatPing)

    async def fileHandle(self) -> None:        
        '''Handle File Updating'''

        while True:   
            state.log("Client Files Reupdated")
            
            #Open and store data to each file                            
            with open(f"client_data/uuid_map/{state.clientProfile}.json", 'w') as uuidHandle:
                json.dump(state.uuidsFile, uuidHandle, indent=4)

            with open(f"client_data/rooms/{state.clientProfile}.json", 'w') as roomHandle:
                json.dump(state.roomsFile, roomHandle, indent=4)
            
            await asyncio.sleep(self.fileIOFrequency)

#__MAIN__
chat_client = ChatClient()