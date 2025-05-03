# Header
import json
import asyncio
import websockets
import argparse

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
    def __init__(self, clientProfile, user_uuid):
        state.enable_roomHandler(clientProfile)   
        state.clientUUID= user_uuid

        self.heartbeatPing = 20
        self.fileIOFrequency = 30
        self.serverAddress = "ws://localhost:8765"
        self.clientProfile = clientProfile

    async def connectClient(self) -> None: 
        async with websockets.connect(self.serverAddress) as clientSocket:   
            await clientSocket.send(json.dumps({"sender": state.clientUUID, "type":"con"}))

            state.log(f"CONNECTED TO SERVER AT: {self.serverAddress}")

            state.clientSock = clientSocket      
            asyncio.create_task(self.fileHandle())

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
            async for dataReceived in state.clientSock:
                response = json.loads(dataReceived)
                state.log(f"Received from Server: {response} \n")

                interface.parse_response(response) 
                
                print()

        except websockets.ConnectionClosedError:
            await self.closeServer()
            
    async def sendPayload(self, payload: tuple) -> None:  #To avoid Client Crash due to Down Server
        '''Payload : ( Message, Type )'''
        try: 
            state.log(f"Sending Payload: {payload} \n")
            await state.clientSock.send(state.encode(payload))

        except websockets.ConnectionClosedError:
            await self.closeServer()
   

    '''------------------------------------------------'''

         
    async def heartbeat(self) -> None:
        while True:            
            await self.sendPayload( ('', state.msgTypes['heartbeat']) )
            await asyncio.sleep(self.heartbeatPing)
    
    async def closeClient(self) -> None:
        state.log("Program Exited")     
        await state.clientSock.close()
        for task in asyncio.all_tasks():
            task.cancel()
            return

    async def closeServer(self) -> None:
        state.log("Server Down")
        print("SERVER DOWN!")
        await self.closeClient()
        return
   

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
    user_uuid = auth.start_auth()

    parser = argparse.ArgumentParser()
    parser.add_argument('--profile', type=str, required=True)
    args = parser.parse_args()

    state.log(f"Event Loop started w/ Profile {args.profile} and UUID {user_uuid}")
    
    client = ChatClient(args.profile, user_uuid)

    try:
        await client.connectClient()
    # i.e., tasks have been cancelled, program exit
    except (asyncio.CancelledError, ConnectionRefusedError, asyncio.TimeoutError):
        pass
        
#__MAIN__
asyncio.run(eventLoop())