class chatClient:

    def __init__(self):
        self.clientUsrn = ''
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSock:        
            self.clientUsrn = input("\nENTER USERNAME: ")
            await clientSock.send(self.clientUsrn)          #Manually encoded within server

            await asyncio.gather(self.send(clientSock), self.receive(clientSock))


    async def send(self,clientSock):
        while True:
            msg = await asyncio.to_thread(input)

            try:
                await clientSock.send(self.encode(msg, 'msg'))

            except websockets.exceptions.ConnectionClosed:
                print("SERVER DOWN") 
                break

    async def receive(self, clientSock):  

        try:
            async for reply in clientSock:  
                # print(reply)                
                response = json.loads(reply)
                match response['type']:
                    case 'msg':
                        print(f"{response['sender']}: {response['content']}")        
                          

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")

    def encode(self, content, type):
        return json.dumps({"sender": self.clientUsrn, "content": content, "type": type})

#__MAIN__
import asyncio
import websockets
import json
client = chatClient()

'''
Message Format: {"sender": <username>, "content": '--', "type": 'msg/..'}
'''