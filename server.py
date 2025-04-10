class chatServer:

    def __init__(self):
        self.clients = {}
        self.users = {}
        asyncio.run(self.start())  
        

    async def start(self):
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")
            await asyncio.Future()  #while True: but with 0 CPU usage
            
        
    async def handleClient(self, clientSock):
        await self.receive(clientSock)


    async def receive(self, clientSock):
        async for dataRecv in clientSock:   
            response = json.loads(dataRecv)

            match response['type']:
                case 'usr':
                    self.clients[clientSock] = response['sender']
                    self.users[response['sender']] = clientSock
                    
                    destination = response['receiver']
                    await self.broadcast(clientSock, self.dataEncode(response), destination)

                case 'msg':
                    destination = response['receiver']
                    await self.broadcast(clientSock, self.dataEncode(response), destination)


    async def broadcast(self, clientSock, dataSend:str, destination):
        if(destination=='.'):
            for client in self.clients:
                if(client != clientSock):
                    await client.send(dataSend)
            return         
        
        await self.users[destination].send(dataSend)

    
    async def userAlerts(self, clientSock, msg):
        await clientSock.send(msg)    
    
    
    def dataEncode(self, response):
        response.pop('receiver')
        return json.dumps(response)



#Run
import asyncio
import websockets
import json
server = chatServer()

''' 
Broadcast sends Data to Everyone but Current Client; userAlerts sends only to current Client
Broadcast tells others about user Actions which the user themselves know and need not be notified 
'''