class chatServer:

    def __init__(self):        
        self.usernames = {}       # username : socket
        self.Sclients= {}         # socket : username
        self.timeout= {}          # socket: last heartbeat
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
            '''
            Variables: 
            dataRecv-> Raw String Data Obtained
            response-> Decoded String to Dictionary Data
            data    -> Data for modification purpose
            reply   -> Modified Data to send if Required Modification
            '''

            async for dataRecv in clientSock:   
                response = json.loads(dataRecv)

                match response['type']:
                    case 'usr':
                        self.usernames[response['sender']] = clientSock
                        self.Sclients[clientSock] = response['sender']
                        
                        await self.broadcast(clientSock, dataRecv, '.')
                    
                    case 'sys':
                        if(response['content'] == '/e'):
                            self.disconnectionPending+= (clientSock,)

                        elif(response['content'] == '/o'):
                            data = list(self.usernames.keys())
                            data.remove(response['sender'])
                            data = '\n'.join(data)

                            reply = json.dumps({'content': data, 'type':'sys'})
                            await self.userAlerts(clientSock, reply)

                    case 'hbp':
                        self.timeout[clientSock] = time.time()

                    case 'msg':
                        destinationU = response['receiver']
                        response.pop('receiver')

                        reply =json.dumps(response)
                        await self.broadcast(clientSock, reply, destinationU)

        except websockets.exceptions.ConnectionClosed:
            print("CLOSED")

    async def broadcast(self, clientSock, dataSend, destinationU):
        if(destinationU=='.'):
            self.clientIteration = True
            for client in self.Sclients.values():
                if(client != clientSock):
                    await self.send(client, dataSend)
            self.clientIteration= False
            return      
        
        elif(destinationU not in self.usernames):
            await self.userAlerts(clientSock, json.dumps({"sender":destinationU, "content":"/e", "type":"sys"}))
            return

        await self.send(self.Sclients[destinationU], dataSend)

    async def send(self, receiveClient, dataSend):    # Prevents Server Crash in case of Lingering Ghost Sockets
        try:
            await receiveClient.send(dataSend)
        except websockets.exceptions.ConnectionClosed:
            self.disconnectionPending+= (receiveClient)

    async def userAlerts(self, clientSock, msg):
        await clientSock.send(msg)    


    async def heartbeats(self):
        while True:            
            for client in self.timeout:
                cTime = time.time() - self.timeout[client]                
                if(cTime >= 40):                    
                    self.disconnectionPending+= (client,)                
            
            await asyncio.sleep(25)

    async def uDisconnect(self): 
        while True:
            await asyncio.sleep(10)
            if(not self.clientIteration and self.disconnectionPending):
                for leavingClient in self.disconnectionPending:
                                        
                    await leavingClient.close()              
                
                    dataSend = json.dumps({"sender":self.Sclients[leavingClient], "content": "/e", "type":"sys"})

                    self.usernames.pop(self.Sclients.pop(leavingClient))                    
                    self.timeout.pop(leavingClient)

                    await self.broadcast('', dataSend, '.') #Empty clientSock as it doesn't exist in self.client.values()      
                self.disconnectionPending = ()          

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