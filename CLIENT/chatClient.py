# Header
import json
import asyncio
import websockets
#import logging

import login
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
    def __init__(self):
        self.state = ClientState()
        #logger = logging_setup.setup_log()

        self.heartbeatPing = 20
        self.fileIOFrequency = 30
        self.serverAddress = "ws://localhost:8765"

    async def connectClient(self) -> None: 
        async with websockets.connect(self.serverAddress) as clientSocket:   
            self.state.clientSock = clientSocket       

            await self.userLogin()

            await asyncio.gather(self.message(), self.receive(),self.heartbeat())
            

    async def userLogin(self) -> None:
        # Loop till Succesfully Logged-on to Server
        while True:  
            authContent = login.start_auth()
            '''AuthContent : {
                ACTION: <REG/LOG>, 
                USERNAME: <>,
                PASSWD: <>
                }'''

            # Validate Credentials From Server
            await self.sendPayload( (authContent, self.state.msgTypes['authentication']) )
            response = json.loads(await self.state.clientSock.recv())

            # Check condition of Log-in
            if(login.was_succesful(response)):
                self.state.clientUUID = response['content']
                return
            
            elif(response['content'] == 102):                
                print(f"{{System}}: {self.state.system_codes[102]}")                
                response = json.loads(await self.state.clientSock.recv())

                print(f"{{System}}: {self.state.system_codes[103]}")
                self.state.clientUUID = response['content']
                return
            
            else:
                login.handle_fail(response)
                continue


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

        except websockets.exceptions.ConnectionClosed:
            await self.closeServer()
            
    async def sendPayload(self, payload: tuple) -> None:  #To avoid Client Crash due to Down Server
        '''Payload : ( Message, Type )'''
        try: 
            await self.state.clientSock.send(self.state.encode(payload))

        except websockets.exceptions.ConnectionClosed:
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
            with open("rooms.json", 'w') as roomHandle:
                json.dump({"rooms": list(self.state.clientRoomsFile)}, roomHandle)

            await asyncio.sleep(self.fileIOFrequency)



'''ENTRY POINT FOR CLIENT SETUP'''
async def eventLoop():
    client = ChatClient()

    try:
        await client.connectClient()
    except asyncio.exceptions.CancelledError:       # i.e., tasks have been cancelled, program exit
        pass
        
#__MAIN__
asyncio.run(eventLoop())