class chatServer:

    def __init__(self):        
        self.clients = {}       # username : socket
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
                    self.clients[response['sender']] = clientSock
                    
                    await self.broadcast(clientSock, dataRecv, '.')
                
                case 'sys':
                    if(response['content']=='/e'):
                        self.clients.pop(response['sender'])

                        await self.broadcast(clientSock, dataRecv, '.')
                        
                case 'msg':
                    destination = response['receiver']
                    response.pop('receiver')
                    await self.broadcast(clientSock, json.dumps(response), destination)



    async def broadcast(self, clientSock, dataSend:str, destination):
        if(destination=='.'):
            for client in self.clients.values():
                if(client != clientSock):
                    await client.send(dataSend)
            return         
        
        try:
            await self.clients[destination].send(dataSend)
        except KeyError:
            msg = {"content": f"{destination} IS OFFLINE", "type": "sys"}
            await self.userAlerts(clientSock, json.dumps(msg))

    
    async def userAlerts(self, clientSock, msg):
        await clientSock.send(msg)    



#Run
import asyncio
import websockets
import json
server = chatServer()

''' 
Broadcast sends Data to Everyone but Current Client; userAlerts sends only to current Client
Broadcast tells others about user Actions which the user themselves know and need not be notified 
'''