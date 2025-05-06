# Header
import json
import asyncio
import websockets
import argparse
import requests

import auth
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
    def __init__(self, clientProfile):       
        self.heartbeatPing = 20
        self.fileIOFrequency = 30
        self.serverAddress = "ws://localhost:8765"
        self.clientProfile = clientProfile        
        asyncio.create_task(self.fileHandle())
        
    async def connectClient(self) -> None: 
        self.clientSock = await websockets.connect(self.serverAddress)
        await self.clientSocket.send(json.dumps({"sender": state.clientUUID, "type":"con"}))
        state.log(f"CONNECTED TO SERVER AT: {self.serverAddress}")
              

    async def start_methods(self) -> None:
            await asyncio.gather(self.message(), self.receive(),self.heartbeat())


    '''------------------------------------------------'''


    async def message(self) -> None:
        while True:
            msgInput = await asyncio.to_thread(input)            
            
            if(command_handler.is_command(msgInput)):
                action, payload = command_handler.parse_command(msgInput)
                '''Action: send, exit, None
                  Payload Format: (content, type)'''
                
                # Check what to do to Payload
                match action:
                    case 'send': await self.sendPayload(payload)
                    case 'exit': 
                        await self.sendPayload(
                            ( (state.client_codes['user_exit'], ''), state.msgTypes['system']))
                        await self.closeClient()      
                    case None: pass              
                    case _: raise ValueError(f"●→ INVALID PAYLOAD ACTION RECEIVED: {action}")

            elif(state.receiver):
                await self.sendPayload( (msgInput, state.msgTypes['message']) )

            else:
                print("[!!ERROR: No Destination Chosen]")       
            
            print()

    async def receive(self) -> None:
        try:
            async for dataReceived in self.clientSock:
                response = json.loads(dataReceived)
                state.log(f"Received from Server: {response} \n")

                task = interface.parse_response(response) 
                if(task=='kick'): await self.closeClient()
                
                print()

        except websockets.ConnectionClosedError:            
            await self.reconnectServer()

    async def sendPayload(self, payload: tuple) -> None:  #To avoid Client Crash due to Down Server
        '''Payload : ( Message, Type )'''
        try: 
            state.log(f"Sending Payload: {payload} \n")
            await self.clientSock.send(state.encode(payload))

        except websockets.ConnectionClosedError:
            await self.reconnectServer()        
   

    '''------------------------------------------------'''

         
    async def heartbeat(self) -> None:
        while True:            
            await self.sendPayload( ('', state.msgTypes['heartbeat']) )
            await asyncio.sleep(self.heartbeatPing)
    
    async def closeClient(self) -> None:
        state.log("Program Exited")     
        await self.clientSock.close()
        for task in asyncio.all_tasks():
            try:
                task.cancel()
            except asyncio.CancelledError:
                pass
        return

    async def reconnectServer(self) -> None:
        state.log("Server Down")        

        while True:
            print("Trying to Connect to Server...")
            try:
                await self.connectClient()
                return
                        
            except ConnectionRefusedError:
                await asyncio.sleep(3)
                continue
   

    '''------------------------------------------------'''


    '''Handle File I/O'''
    async def fileHandle(self) -> None:
        while True:   
            state.log("Client Files Reupdated")
            #Open and store data to each file
            with open(f"rooms/{self.clientProfile}.json", 'w') as roomHandle:
                json.dump({"rooms": list(state.clientRoomsFile)}, roomHandle)
            
            await asyncio.sleep(self.fileIOFrequency)



'''ENTRY POINT FOR CLIENT SETUP'''
async def eventLoop():  
    
    # Basic Setup
    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=str, required=True)
    args = parser.parse_args()

    state.profileBased(args.profile)
    client = ChatClient(args.profile)

    state.log(f"Event Loop started w/ Profile {args.profile}")

    # Failure Prone Activities
    try:
        requests.get("http://127.0.0.1:8000/")
        user_uuid = auth.start_auth()

    except requests.exceptions.ConnectionError:
        state.log(f"API Server Failed; Reconnecting")
        await reconnect(client)
        return

    state.log(f"UUID OBTAINED: {user_uuid}")
    state.clientUUID = user_uuid

    try:
        await client.connectClient()   
        pass  
           
    except ConnectionRefusedError:
        await reconnect(client, user_uuid)
        state.log(f"Chat Server Failed; Reconnecting")
        return

async def reconnect(client:ChatClient, uuid: str = None):    
    
    while True:
        print("Trying to Connect to Server...")
        if(not uuid):
            try:
                requests.get("http://127.0.0.1:8000/")
                uuid = auth.start_auth()
            except requests.exceptions.ConnectionError:
                await asyncio.sleep(3)
                continue
            else: 
                state.log(f"UUID OBTAINED: {uuid}")
                state.clientUUID = uuid               
        
        try:
            await client.connectClient()
            return
        
        except ConnectionRefusedError:
            await asyncio.sleep(3)
            continue

        
        
#__MAIN__
asyncio.run(eventLoop())