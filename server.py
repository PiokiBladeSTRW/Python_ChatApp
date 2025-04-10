class chatServer:

    def __init__(self):        
        self.clients = {}       # username : socket
        self.sockets= {}        # socket : username
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
                    self.sockets[clientSock] = response['sender']
                    
                    await self.broadcast(clientSock, dataRecv, '.')
                
                case 'sys':
                    if(response['content']=='/e'):
                        await self.uDisconnect(response['sender'])                       

                case 'msg':
                    destination = response['receiver']
                    response.pop('receiver')
                    await self.broadcast(clientSock, json.dumps(response), destination)



    async def broadcast(self, clientSock, dataSend, destination):
        if(destination=='.'):
            for client in self.clients.values():
                if(client != clientSock):
                    await self.send(client, dataSend)
            return            

        await self.send(self.clients[destination], dataSend)


    async def send(self, receiveClientSk, dataSend):
        try:
            await receiveClientSk.send(dataSend)
        except websockets.exceptions.ConnectionClosed:
            await self.uDisconnect(self.sockets[receiveClientSk])

    
    async def userAlerts(self, clientSock, msg):
        await clientSock.send(msg)    

    async def uDisconnect(self, leavingClient):        #Unintended Disconnection
        await self.clients[leavingClient].close()
        self.sockets.pop(self.clients.pop(leavingClient))       
    
        dataSend = {"sender":leavingClient, "content": "/e", "type":"sys"}

        await self.broadcast('', json.dumps(dataSend), '.') #Empty clientSock as it doesn't exist in self.client.values()


#Run
import asyncio
import websockets
import json
server = chatServer()

''' 
Broadcast sends Data to Everyone but Current Client; userAlerts sends only to current Client
Broadcast tells others about user Actions which the user themselves know and need not be notified 
'''