class chatServer:

    def __init__(self):        
        self.clients = {}       # username : socket
        self.sockets= {}        # socket : username
        self.timeout= {}        # username: last heartbeat

        self.disconnectionPending = ()
        self.clientIteration = False
        asyncio.run(self.start())  
        

    async def start(self):
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")
            await asyncio.Future()  #while True: but with 0 CPU usage
            
        
    async def handleClient(self, clientSock):
        await asyncio.gather(self.receive(clientSock), self.heartbeats(), self.uDisconnect())


    async def receive(self, clientSock):
        try:
            async for dataRecv in clientSock:   
                response = json.loads(dataRecv)

                match response['type']:
                    case 'usr':                   
                        self.clients[response['sender']] = clientSock
                        self.sockets[clientSock] = response['sender']

                        self.timeout[response['sender']] = time.time()
                        
                        await self.broadcast(clientSock, dataRecv, '.')
                    
                    case 'sys':
                        if(response['content'] == '/e'):
                            self.disconnectionPending+= (response['sender'],)

                        elif(response['content'] == '/o'):            
                            data = list(self.clients.keys())
                            data.remove(response['sender'])
                            data = '\n'.join(data)
                            response = json.dumps({'content': data, 'type':'sys'})                            

                            await self.userAlerts(clientSock, response)

                    case 'hbp':
                        self.timeout[response['sender']] = time.time()

                    case 'msg':
                        destination = response['receiver']
                        response.pop('receiver')
                        await self.broadcast(clientSock, json.dumps(response), destination)
        except websockets.exceptions.ConnectionClosed:
            print("CLOSED")


    async def broadcast(self, clientSock, dataSend, destination):
        if(destination=='.'):
            self.clientIteration = True
            for client in self.clients.values():
                if(client != clientSock):
                    await self.send(client, dataSend)
            self.clientIteration= False
            return      
        
        elif(destination not in self.clients):
            await self.userAlerts(clientSock, json.dumps({"sender":destination, "content":"/e", "type":"sys"}))
            return

        await self.send(self.clients[destination], dataSend)


    async def send(self, receiveClientSk, dataSend):    # Prevents Server Crash in case of Lingering Ghost Sockets
        try:
            await receiveClientSk.send(dataSend)
        except websockets.exceptions.ConnectionClosed:
            self.disconnectionPending+= (self.sockets[receiveClientSk],)

    
    async def userAlerts(self, clientSock, msg):
        await clientSock.send(msg)    

    async def uDisconnect(self): 
        while True:
            await asyncio.sleep(10)
            if(not self.clientIteration and self.disconnectionPending):
                for leavingClient in self.disconnectionPending:
                                        
                    await self.clients[leavingClient].close()
                    self.sockets.pop(self.clients.pop(leavingClient))  
                    self.timeout.pop(leavingClient)  
                
                    dataSend = {"sender":leavingClient, "content": "/e", "type":"sys"}

                    await self.broadcast('', json.dumps(dataSend), '.') #Empty clientSock as it doesn't exist in self.client.values()      
                self.disconnectionPending = ()          

    async def heartbeats(self):
        while True:            
            for client in self.timeout:
                cTime = time.time() - self.timeout[client]                
                if(cTime >= 40):                    
                    self.disconnectionPending+= (client,)                
            
            await asyncio.sleep(25)


#Run
import asyncio
import websockets
import json
import time
server = chatServer()

''' 
Broadcast sends Data to Everyone but Current Client; userAlerts sends only to current Client
Broadcast tells others about user Actions which the user themselves know and need not be notified 
'''