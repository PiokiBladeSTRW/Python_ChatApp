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
            self.clientSock = clientSocket             

            self.clientUsrn = input("\nENTER USERNAME: ").strip()

            await self.send("", "usr")

            try:
                await asyncio.gather(self.message(), self.receive(),self.heartbeat())
            except asyncio.exceptions.CancelledError:       # i.e., tasks have been cancelled, program exit
                pass


    async def receive(self):
        try:
            async for response in self.clientSock:                  
                response = json.loads(response)        
                if(response.get('timestamp')):
                    response['timestamp'] = time.strftime("%H:%M", time.localtime(float(response['timestamp'])))                              

                if(response['type'] == 'msg'):
                    if(response['sender'] == self.receiver):
                        print(f"[{response['timestamp']}]> {response['content']}\n")                         
                        continue

                    if(response['sender'].startswith('[')): #AKA Room Message, and Room messages are only sent to Members
                        print(f"[{response['timestamp']}] {response['sender']}: {response['content']}\n")
                        continue

                    print(f"< {response['sender']}: {response['content']} >")   # Outsider Message

                elif(response['type'] == 'usr'):
                    print(f"[{response['sender']} is ONLINE]") 
                
                elif(response['type'] == 'sys'):        

                    #If Else to allow System to Manipulate Clients
                    if(response['content'] == '/e'):
                        print(f"[{response['sender']} is OFFLINE]")
                        if(self.receiver == response['sender']): self.receiver = ''
                    else:
                        print(f"{{System}}: {response['content']}")
                
                print()

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")
            await self.disconnect()

    async def message(self):
        while True:
            msg = await asyncio.to_thread(input, ">>")

            if(commands.is_command(msg)):
                action, payload, state = commands.parse_command(msg, state)
                
                match action:
                    case 'send': await self.send(payload)
                    case 'exit': await self.disconnect()
                    case None: pass
                    case _: raise Exception("●→ INVALID ACTION RECEIVED")                

            else:                              
                if(self.receiver):
                    await self.send(msg, 'msg')

                else:
                    print("[!!ERROR: No Destination Chosen]")   

            print()             

    async def send(self, payload):
        try:            
            await self.clientSock.send(utils.encode(payload))

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN") 
            await self.disconnect()


    async def heartbeat(self):
        while True:
            await self.send('', 'hbp')
            await asyncio.sleep(20)
    
    async def disconnect(self):
        await self.send('/e', 'sys')
        await self.clientSock.close()
        for task in asyncio.all_tasks():
            task.cancel()
            return
        
#__MAIN__
import asyncio
import websockets
import json
import time

import commands
import utils

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