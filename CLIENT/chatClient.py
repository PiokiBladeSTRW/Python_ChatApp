class chatClient:
    '''Initialization'''
    def __init__(self):
        self.state = clientState()
        self.heartbeatPing = 20
        self.serverAddress = "ws://localhost:8765"

    async def connectStartup(self):
        async with websockets.connect(self.serverAddress) as clientSocket:   
            self.state.clientSock = clientSocket       

            # Handle Session Log-in
            await self.login()

            #Start Client up
            try:
                await asyncio.gather(self.message(), self.receive(),self.heartbeat())
            except asyncio.exceptions.CancelledError:       # i.e., tasks have been cancelled, program exit
                pass

    async def login(self):
        while True:  
            '''AuthContent : {ACTION: <REG/LOG>, USERNAME: <>, PASSWD: <>}'''  

            authContent = login.begin_process()
            await self.send((authContent, self.state.msgTypes['authentication']))
            response = json.loads(await self.state.clientSock.recv())
            
            if(response['content']==True):
                self.state.clientUsrn = authContent['username']
                await self.send(('', 'usr'))
                return
            
            print(f"{{System}}: {response['content']}")
            continue


    '''Obtain and Send Data'''
    async def message(self):
        while True:
            msgInput = await asyncio.to_thread(input)

            if(command_handler.is_command(msgInput)):
                
                ''' Payload Format: (content, type)'''
                action, payload, self.state = command_handler.parse_command(msgInput, self.state)
                
                #Check what to do to Payload
                match action:
                    case 'send': await self.send(payload)
                    case 'exit': 
                        await self.send(('/e', self.state.msgTypes['system']))
                        await self.close()
                    #Remove following two lines later, purely testing purpose
                    case None: pass
                    case _: raise Exception("●→ INVALID PAYLOAD ACTION RECEIVED")

            elif(self.state.receiver):                           
                await self.send( (msgInput, self.state.msgTypes['message']) )

            else:
                print("[!!ERROR: No Destination Chosen]")       
            
            print()

    async def send(self, payload):  #To avoid Client Crash due to Down Server
        try: 
            await self.state.clientSock.send(utils.encode(payload, self.state))
        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN") 
            await self.close()

    async def receive(self):
        try:
            async for dataReceived in self.state.clientSock:
                response = json.loads(dataReceived)                   

                self.state = interface.parse_response(response, self.state) 
                
                print()

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")
            await self.close()


    '''Handle Disconnection'''
    async def heartbeat(self):
        while True:
            await self.send( ('', self.state.msgTypes['heartbeat']) )
            await asyncio.sleep(self.heartbeatPing)
    
    async def close(self):        
        await self.state.clientSock.close()
        for task in asyncio.all_tasks():
            task.cancel()
            return

async def eventLoop():
    client = chatClient()
    await client.connectStartup()
        
#__MAIN__
# Design Note: snakeCase in main classes, seperator_case in module
import asyncio
import websockets
import json

import login
import command_handler
import utils
import interface
from session_state import clientState

#To avoid Creating Event Loop within the Class instead of the Class within the Event Loop
asyncio.run(eventLoop())

'''
Message Format: {"sender": <username>, 
                "receiver": <username>, 
                "content": '--', 
                "type": 'msg/..',
                "timestamp": "[Hour:Minute]"}        
'''