class chatClient:

    def __init__(self):
        self.clientUsrn = ''
        self.receiver = '.'             #Defaults to All Clients to Display <> is ONLINE
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSock:      

            self.clientUsrn = input("\nENTER USERNAME: ")
            await clientSock.send(self.encode("is ONLINE", "usr"))
            self.receiver = ''

            await asyncio.gather(self.message(clientSock), self.receive(clientSock))


    async def message(self, clientSock):
        while True:
            msg = await asyncio.to_thread(input)

            '''Match Command'''
            if(msg.startswith('/dm')):
                self.receiver = msg.split()[1]
                msg = msg[msg.find(self.receiver)+len(self.receiver)+1::]
                await self.send(clientSock, self.encode(msg, 'msg'))

            elif(msg.startswith('/@')):
                self.receiver= msg[3::] #As '/@ ' are 3 char

            elif(msg.startswith('/#')):
                self.receiver= ''

            else:
                if(self.receiver):
                    await self.send(clientSock, self.encode(msg, 'msg'))
                else:
                    print("[ERROR: No Destination Chosen]")


    async def receive(self, clientSock):
        try:
            async for response in clientSock:                              
                response = json.loads(response)
                
                match response['type']:                    
                    case 'msg'|'usr':
                        print(f"{response['sender']}: {response['content']}") 

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")

    async def send(self, clientSock, encMsg):
        try:
            await clientSock.send(encMsg)

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN") 


    def encode(self, content, type):
        #Before returning, Content should be encoded
        return json.dumps({"sender": self.clientUsrn, "receiver": self.receiver, "content": content, "type": type})

    

#__MAIN__
import asyncio
import websockets
import json
client = chatClient()

'''
Message Format: {"sender": <username>, "receiver": <username>, "content": '--', "type": 'msg/..'}
Types:
->msg: String Message, most common type
->usr: Entry of Username / Retrieval of '<> IS ONLINE'
'''