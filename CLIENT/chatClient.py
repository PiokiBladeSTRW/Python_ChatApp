# Header
import json
import asyncio
import aioconsole
import websockets

import commands.command_handler as command_handler
import interface
from session_state import state

'''
The Client Object
Purpose: The primary handler of the Client's Activity
Acitivities:
    Handling the Usage of Modules
    Connecting to Server
    Logging-In    
    Receiving and Sending Messages
    Heartbeats & Elegant Disconnection during Crash
'''
class ChatClient:    
    def __init__(self):       
        self.heartbeatPing = 20
        self.fileIOFrequency = 30
        self.serverAddress = "ws://localhost:8765"     
        self.exit_code = None               
        
    async def connectClient(self) -> None: 
        self.clientSock = await websockets.connect(self.serverAddress)
        await self.clientSock.send(json.dumps({"sender_id": state.clientUUID, "type":"con"}))    
        state.log(f"CONNECTED TO SERVER AT: {self.serverAddress}")     

        asyncio.create_task(self.fileHandle())        
        print("Connected to Server! ")        

    async def start_methods(self) -> None:
        tasks = [
            asyncio.create_task(self.message()),
            asyncio.create_task(self.receive()),
            asyncio.create_task(self.heartbeat())
        ]
        state.log(f"Starting Co-routines")
        #Remove var later
        useless_var = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        state.log("Program Exited")     
        await self.clientSock.close()

        # Cancel The
        for task in asyncio.all_tasks():            
            if(task != asyncio.current_task()):
                task.cancel()
                try: await task
                except asyncio.CancelledError: pass
        
        return self.exit_code


    '''------------------------------------------------'''


    async def message(self) -> None:    
        state.log(f"Message Up & Running")
        while True:            
            msgInput = await aioconsole.ainput()            
            
            if(command_handler.is_command(msgInput)):
                action, payload = command_handler.parse_command(msgInput)
                '''Action: send, exit, None
                  Payload Format: (content, type)'''
                
                # Check what to do to Payload
                match action:
                    case 'send': self.exit_code = await self.sendPayload(payload)
                    case 'exit': 
                        self.exit_code = await self.sendPayload(
                            ((state.client_codes['user_exit'], ''), state.msgTypes['system']) )                        
                        self.exit_code = 0                        
                    case None: pass              
                    case _: raise ValueError(f"●→ INVALID PAYLOAD ACTION RECEIVED: {action}")

            elif(state.receiver_id):
                self.exit_code = await self.sendPayload( (msgInput, state.msgTypes['message']) )

            else:
                print("[!!ERROR: No Destination Chosen]")       
            
            if(self.exit_code): return

            print()

    async def receive(self) -> None:
        state.log(f"Receive Up & Running")
        try:
            async for dataReceived in self.clientSock:
                response = json.loads(dataReceived)
                state.log(f"Received from Server: {response} \n")

                task = interface.parse_response(response) 
                if(task=='kick'):                     
                    self.exit_code= 0
                
                print()

        except websockets.ConnectionClosedError: 
            state.log(f"Server Closed")
            self.exit_code = 1
            return 

    async def sendPayload(self, payload: tuple) -> None:  #To avoid Client Crash due to Down Server
        '''Payload : ( Message, Type )'''
        try: 
            state.log(f"Sending Payload: {payload} \n")
            await self.clientSock.send(state.encode(payload))

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
   

    '''------------------------------------------------'''


    '''Handle File I/O'''
    async def fileHandle(self) -> None:
        while True:   
            state.log("Client Files Reupdated")
            
            #Open and store data to each file                            
            with open(f"client_data/uuid_map/{state.clientProfile}.json", 'w') as uuidHandle:
                json.dump(state.uuidsFile, uuidHandle)
            
            await asyncio.sleep(self.fileIOFrequency)

#__MAIN__
client = ChatClient()