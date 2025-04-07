class chatServer:

    def __init__(self):
        self.clients = {}   
        asyncio.run(self.start())  
        
    async def start(self):
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")
            await asyncio.Future()  #while True: but with 0 CPU usage
        
    async def handleClient(self, clientSock):
        usrname = await clientSock.recv()
        self.clients[clientSock] = usrname

        await self.broadcast(clientSock, f"[{self.clients[clientSock]} IS ONLINE]")

        await self.receive(clientSock)

    async def receive(self, clientSock):
        async for message in clientSock:
            print(message)

            await self.broadcast(clientSock, f"{self.clients[clientSock]}: {message}")

    async def broadcast(self, clientSock, msg):
        for client in self.clients:
            if (client != clientSock):
                await client.send(msg)
    
    async def userAlerts(self, clientSock, msg):
        await clientSock.send(msg)

    ''' 
    Broadcast sends Data to Everyone but Current Client; userAlerts sends only to current Client
    Broadcast tells others about user Actions which the user themselves know and need not be notified 
    '''

#Run
import asyncio
import websockets
server = chatServer()