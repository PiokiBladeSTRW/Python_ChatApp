class chatClient:

    def __init__(self):
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSock:        
            usrn = input("\nENTER USERNAME: ")
            await clientSock.send(usrn)

            await asyncio.gather(self.send(clientSock), self.receive(clientSock))

    async def send(self,clientSock):
        while True:
            msg = await asyncio.to_thread(input)
            try:
                await clientSock.send(msg)
            except websockets.exceptions.ConnectionClosed:
                print("SERVER DOWN") 
                break

    async def receive(self, clientSock):
        try:
            async for reply in clientSock:
                print(reply)
        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN")

#__MAIN__
import asyncio
import websockets
client = chatClient()