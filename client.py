class chatClient:

    def __init__(self):
        self.clientUsrn = ''
        self.receiver = '.'             #Defaults to All Clients to Display <> is ONLINE
        self.clientSock = None
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSocket:   
            self.clientSock = clientSocket 

            self.clientUsrn = input("\nENTER USERNAME: ")
            await self.clientSock.send(self.encode("", "usr"))
            self.receiver = ''

            await asyncio.gather(self.message(), self.receive())


    async def message(self):
        while True:
            msg = await asyncio.to_thread(input)

            '''Check for Command'''
            
            if(msg.startswith('/dm')):          # Dm Selection
                data = msg.split()
                self.receiver= data[1]
                msg = ' '.join(data[2::])

                await self.send(self.encode(msg, 'msg'))

            elif(msg.startswith('/#')):         # DM Removal
                self.receiver= ''

            else:                               # No Commands
                if(self.receiver):
                    await self.send(self.encode(msg, 'msg'))
                else:
                    print("[!!ERROR: No Destination Chosen]")


    async def receive(self):
        try:
            async for response in self.clientSock:                              
                response = json.loads(response)

                if(response['type'] == 'msg'):
                    print(f"{response['sender']}: {response['content']}") 

                elif(response['type'] == 'usr'):
                    print(f"[{response['sender']} is ONLINE]") 

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")


    async def send(self, encMsg):
        try:
            await self.clientSock.send(encMsg)

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN") 



    def encode(self, content, type):
        #Before returning, Content should be encoded
        return json.dumps({"sender": self.clientUsrn, 
                           "receiver": self.receiver, 
                           "content": content, ""
                           "type": type})

    

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