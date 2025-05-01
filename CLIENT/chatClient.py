# Header
import json
import asyncio
import websockets
import argparse
#import logging

import auth
import commands.command_handler as command_handler
import interface
#import logging_setup
from session_state import ClientState

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
    def __init__(self, clientProfile, user_uuid):
        self.state = ClientState(clientProfile)        
        #logger = logging_setup.setup_log()

        self.state.clientUUID= user_uuid
        self.heartbeatPing = 20
        self.fileIOFrequency = 30
        self.serverAddress = "ws://localhost:8765"
        self.clientProfile = clientProfile

    async def connectClient(self) -> None: 
        async with websockets.connect(self.serverAddress) as clientSocket:   
            self.state.clientSock = clientSocket       

            asyncio.create_task(self.fileHandle())

            await asyncio.gather(self.message(), self.receive(),self.heartbeat())


    '''------------------------------------------------'''


    async def message(self) -> None:
        while True:
            msgInput = await asyncio.to_thread(input)

            if(command_handler.is_command(msgInput)):
                action, payload, self.state = command_handler.parse_command(msgInput, self.state)
                '''Action: send, exit, None
                  Payload Format: (content, type)'''
                
                # Check what to do to Payload
                match action:
                    case 'send': await self.sendPayload(payload)
                    case 'exit': 
                        await self.sendPayload(
                            ( (self.state.client_codes['user_exit'], ''), self.state.msgTypes['system']))
                        await self.closeClient()      
                    case None: pass              
                    case _: raise ValueError(f"●→ INVALID PAYLOAD ACTION RECEIVED: {action}")

            elif(self.state.receiver):
                await self.sendPayload( (msgInput, self.state.msgTypes['message']) )

            else:
                print("[!!ERROR: No Destination Chosen]")       
            
            print()

    async def receive(self) -> None:
        try:
            async for dataReceived in self.state.clientSock:
                response = json.loads(dataReceived)

                self.state = interface.parse_response(response, self.state) 
                
                print()

        except websockets.ConnectionClosedError:
            await self.closeServer()
            
    async def sendPayload(self, payload: tuple) -> None:  #To avoid Client Crash due to Down Server
        '''Payload : ( Message, Type )'''
        try: 
            await self.state.clientSock.send(self.state.encode(payload))

        except websockets.ConnectionClosedError:
            await self.closeServer()
   

    '''------------------------------------------------'''

         
    async def heartbeat(self) -> None:
        while True:
            await self.sendPayload( ('', self.state.msgTypes['heartbeat']) )
            await asyncio.sleep(self.heartbeatPing)
    
    async def closeClient(self) -> None:        
        await self.state.clientSock.close()
        for task in asyncio.all_tasks():
            task.cancel()
            return

    async def closeServer(self) -> None:
        print("SERVER DOWN!")
        await self.closeClient()
        return
   

    '''------------------------------------------------'''


    '''Handle File I/O'''
    async def fileHandle(self) -> None:
        while True:   
            
            #Open and store data to each file
            with open(f"rooms/{self.clientProfile}.json", 'w') as roomHandle:
                json.dump({"rooms": list(self.state.clientRoomsFile)}, roomHandle)
            
            await asyncio.sleep(self.fileIOFrequency)



'''ENTRY POINT FOR CLIENT SETUP'''
async def eventLoop():
    user_uuid = auth.start_auth()

    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=str, required=True)
    args = parser.parse_args()

    client = ChatClient(args.profile, user_uuid)

    try:
        await client.connectClient()
    # i.e., tasks have been cancelled, program exit
    except (asyncio.CancelledError, ConnectionRefusedError, asyncio.TimeoutError):
        pass
        
#__MAIN__
asyncio.run(eventLoop())