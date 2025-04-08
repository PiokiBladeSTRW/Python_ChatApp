class chatClient:

    def __init__(self):
        self.clientUsrn = ''
        self.lock = asyncio.Lock()
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSock:        
            self.clientUsrn = input("\nENTER USERNAME: ")
            await clientSock.send(self.encode("IS ONLINE", "usr"))

            await self.chooseCon(clientSock)

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
                            
                response = json.loads(reply)
                match response['type']:
                    case 'msg'|'usr':
                        print(f"{response['sender']}: {response['content']}") 

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")

    async def chooseCon(self, clientSock):
        async def onlineDisp():
            response= json.loads(await clientSock.recv())
            print(f"{response['sender']}: \n{response['content']}") 

            return response['content'].split('\n')

        async with self.lock:
            onlineList = await onlineDisp()

            while True:            
                choice = int(input("->"))

                if(choice < len(onlineList)):
                    choice = onlineList[choice]
                    await clientSock.send(self.encode(choice, 'onl'))
                    break

                elif(choice == len(onlineList)):                    
                    await clientSock.send(self.encode('%', 'usr'))
                    await asyncio.sleep(3)

                    onlineList=  await onlineDisp()

                else:
                    continue

    def encode(self, content, type):
        #Before returning, Content should be encoded
        return json.dumps({"sender": self.clientUsrn, "content": content, "type": type})
    





#__MAIN__
import asyncio
import websockets
import json
client = chatClient()

'''
Message Format: {"sender": <username>, "content": '--', "type": 'msg/..'}
Types:
->msg: String Message, most common type
->usr: Entry of Username / Retrieval of Online
->onl: Retrieval of Entire Online List
'''