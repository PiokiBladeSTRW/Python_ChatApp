class chatClient:
    '''Initialization'''
    def __init__(self):
        self.state = clientState()
        print(self.state.clientUsrn, self.state.receiver)
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSocket:   
            self.state.clientSock = clientSocket       

            # Handle Session Log-in
            while True:     
                content = login.begin_process()
                await self.send((content, 'auth'))
                response = json.loads(await clientSocket.recv())
                
                if(response['content']==True):
                    self.state.clientUsrn = content['username']
                    break
                print(f"{{System}}: {response['content']}")
                continue

            

            self.state.clientUsrn = input("\nENTER USERNAME: ").strip()

            await self.send( ("", "usr") )

            try:
                await asyncio.gather(self.message(), self.receive(),self.heartbeat())
            except asyncio.exceptions.CancelledError:       # i.e., tasks have been cancelled, program exit
                pass

    '''Obtain and Send Data'''
    async def message(self):
        while True:
            msg = await asyncio.to_thread(input)

            if(command_handler.is_command(msg)):
                
                ''' Payload Format: (content, type)'''
                action, payload, self.state = command_handler.parse_command(msg, self.state)
                
                #Check what to do to Payload
                match action:
                    case 'send': await self.send(payload)
                    case 'exit': 
                        await self.send(('/e', 'sys'))
                        await self.close()
                    case None: pass
                    case _: raise Exception("●→ INVALID PAYLOAD ACTION RECEIVED")

            elif(self.state.receiver):                           
                await self.send( (msg, 'msg') )

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
            async for response in self.state.clientSock:
                response = json.loads(response)                   

                self.state = interface.parse_response(response, self.state) 
                
                print()

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")
            await self.close()


    '''Handle Disconnection'''
    async def heartbeat(self):
        while True:
            await self.send( ('', 'hbp') )
            await asyncio.sleep(20)
    
    async def close(self):        
        await self.state.clientSock.close()
        for task in asyncio.all_tasks():
            task.cancel()
            return
        
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

client = chatClient()

'''
Message Format: {"sender": <username>, 
                "receiver": <username>, 
                "content": '--', 
                "type": 'msg/..',
                "timestamp": "[Hour:Minute]"}        
'''