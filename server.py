class chatServer:

    def __init__(self):
        self.clients = {}
        asyncio.run(self.start())  
        

    async def start(self):
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")
            await asyncio.Future()  #while True: but with 0 CPU usage
        
    async def handleClient(self, clientSock):
        self.clients.append(clientSock)

        await self.userAlerts(clientSock, json.dumps({'sender': 'sys', 'content': '\n'.join(self.clients.values()), 'type':'onl'}))

        await self.receive(clientSock)


    async def receive(self, clientSock):
        async for dataRecv in clientSock:
            print(dataRecv)

            decodedData= json.loads(dataRecv)
            match decodedData['type']:
                case 'usr': self.clients[clientSock] = decodedData['sender']
                case _ : pass

            del decodedData
            ''' Check whether the given data is a Special Case or Not '''              

            await self.broadcast(clientSock, dataRecv)

    async def broadcast(self, clientSock, dataRecv:str):
        for client in self.clients:
            if (client != clientSock):
                await client.send(dataRecv)
    
    async def userAlerts(self, clientSock, msg):
        await clientSock.send(msg)

    ''' 
    Broadcast sends Data to Everyone but Current Client; userAlerts sends only to current Client
    Broadcast tells others about user Actions which the user themselves know and need not be notified 
    '''

#Run
import asyncio
import websockets
import json
server = chatServer()