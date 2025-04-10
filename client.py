class chatClient:

    def __init__(self):
        self.clientUsrn = ''
        self.receiver = ''             #Defaults to All Clients to Display <> is ONLINE
        self.clientSock = None
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSocket:   
            self.clientSock = clientSocket 

            self.clientUsrn = input("\nENTER USERNAME: ")
            await self.clientSock.send(self.encode("", "usr"))

            try:
                await asyncio.gather(self.message(), self.receive())
            except asyncio.exceptions.CancelledError:
                pass


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

            elif(msg.startswith('/e')):
                await self.send(self.encode('/e', 'sys'))
                await self.clientSock.close()               
                for task in asyncio.all_tasks():
                    task.cancel()
                    return

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
                
                elif(response['type'] == 'sys'):
                    #If Else to allow System to Manipulate Clients
                    if(response['content'] == '/e'):
                        print(f"[{response['sender']} is OFFLINE]")
                        if(self.receiver == response['sender']): self.receiver = ''

                    else:
                        print(f"SYSTEM: {response['content']}")

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")


    async def send(self, encMsg):
        try:
            await self.clientSock.send(encMsg)

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN") 



    def encode(self, content, type):
        #Before returning, Content should be encoded
        if(type in ('usr', 'sys')):
            return json.dumps({"sender": self.clientUsrn, 
                           "content": content, ""
                           "type": type})

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
->sys: System Message and/or Special Instructions
'''