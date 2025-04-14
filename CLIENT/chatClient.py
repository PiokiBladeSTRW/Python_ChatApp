class chatClient:

    def __init__(self):
        self.state= {
            'clientUsrn' : '',
            'receiver' : '',
            'pReceiver' : '', 
            'clientSock' : None
            }

        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSocket:   
            self.state['clientSock'] = clientSocket             

            self.state['clientUsrn'] = input("\nENTER USERNAME: ").strip()

            await self.send( ("", "usr") )

            try:
                await asyncio.gather(self.message(), self.receive(),self.heartbeat())
            except asyncio.exceptions.CancelledError:       # i.e., tasks have been cancelled, program exit
                pass


    async def receive(self):
        try:
            async for response in self.state['clientSock']:
                response = json.loads(response)   

                self.state = interface.parse_response(response, self.state) 
                
                print()

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")
            await self.close()

    async def message(self):
        while True:
            msg = await asyncio.to_thread(input, ">>")

            if(commands.is_command(msg)):
                action, payload, self.state = commands.parse_command(msg, self.state)
                
                match action:
                    case 'send': await self.send(payload)
                    case 'exit': 
                        await self.send('/e', 'sys')
                        await self.close()
                    case None: pass
                    case _: raise Exception("●→ INVALID ACTION RECEIVED")                

            else:                              
                if(self.state['receiver']):
                    await self.send(msg, 'msg')
                else:
                    print("[!!ERROR: No Destination Chosen]") 

            print()             

    async def send(self, payload):
        try:            
            await self.state['clientSock'].send(utils.encode(payload))

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN") 
            await self.close()

    async def heartbeat(self):
        while True:
            await self.send( ('', 'hbp') )
            await asyncio.sleep(20)
    
    async def close(self):        
        await self.state['clientSock'].close()
        for task in asyncio.all_tasks():
            task.cancel()
            return
        
#__MAIN__
import asyncio
import websockets
import json
import time     #Every Module depends on this

import commands
import utils
import interface

client = chatClient()


'''
Message Format: {"sender": <username>, 
                "receiver": <username>, 
                "content": '--', 
                "type": 'msg/..',
                "timestamp": "[Hour:Minute]"}        
'''

''' Payload Format: (content, type)'''

'''snakeCase in main classes, seperator_case in module'''