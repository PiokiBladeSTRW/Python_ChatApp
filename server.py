class chatServer:

    def __init__(self):        
        self.usernames = {}             # username : socket
        self.clients= {}                # socket : username
        self.timeout= {}                # socket: last heartbeat        
        self.rooms= {}                  # room name : [sockets]
        self.disconnectionPending = asyncio.Queue()
        #self.clientIteration = False

        asyncio.run(self.start())

    async def start(self):
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")
            await asyncio.Future()  #while True: but with 0 CPU usage            
        
    async def handleClient(self, clientSock):
        await asyncio.gather(self.receive(clientSock), self.heartbeats(), self.Disconnect())



    async def receive(self, clientSock):
        try:
            '''
            Variables: 
            dataRecv-> Raw String Data Obtained
            response-> Decoded String to Dictionary Data
            data    -> Data for modification purpose
            dataSent-> Modified Data to send if Required Modification
            '''

            async for dataRecv in clientSock:   
                response: dict = json.loads(dataRecv)               

                match response['type']:
                    case 'usr':
                        self.usernames[response['sender']] = clientSock
                        self.clients[clientSock] = response['sender']
                        
                        await self.broadcast(clientSock, dataRecv, '.')
                    
                    case 'sys':
                        if(response['content'] == '/e'):
                            await self.disconnectionPending.put(clientSock)

                        elif(response['content'] == '/o'):                            
                            data = list(self.usernames.keys())
                            data.remove(response['sender'])
                            data = '\n'.join(data)

                            dataSend = json.dumps({'content': data, 'type':'sys'})
                            await self.userAlerts(clientSock, dataSend)
                        
                        elif(response['content'] == '/r'):
                            data = '\n'.join(self.rooms.keys())

                            dataSend = json.dumps({'content': data, 'type': 'sys'})
                            await self.userAlerts(clientSock, dataSend)
                        
                        elif(response['content'].startswith('/c')):                            
                            data = response['content'][2::]
                            self.rooms[data] = [ self.usernames[response['sender']] ]

                            dataSend = json.dumps({'content': f"Room {data} Is Live", "type":"sys"})
                            await self.userAlerts(clientSock, dataSend)

                    case 'hbp':
                        self.timeout[clientSock] = time.time()           

                    case 'msg': 
                        destinationU = response['receiver']
                        response.pop('receiver')

                        room = ''
                        if(destinationU.startswith('/r')):                  # Room Handling      
                            room= destinationU[2::]                     
                            if(room not in self.rooms):
                                dataSend = json.dumps({"content": "[INVALID ROOM]", "type": "sys"})
                                await self.userAlerts(clientSock, dataSend)
                                continue
                            
                            if(clientSock not in self.rooms[room]):
                                self.rooms[room].append(clientSock)
                            
                            response['sender'] = f"[{room}] {response['sender']}"
                            destinationU = ''                               #Empty Destination as it's useless

                        dataSend =json.dumps(response)
                        await self.broadcast(clientSock, dataSend, destinationU, room)    

        except websockets.exceptions.ConnectionClosed:
            print("CLOSED")

    async def broadcast(self, clientSock, dataSend:str, destinationU:str, room= ''):
        if(destinationU=='.'):
            #self.clientIteration = True
            for client in list(self.clients):
                if(client != clientSock):
                    await self.send(client, dataSend)
            #self.clientIteration= False
            return     

        elif(room):
            #self.clientIteration = True
            for client in list(self.rooms[room]):
                if(client != clientSock):
                    await self.send(client, dataSend)
            #self.clientIteration = False
            return
        
        elif(destinationU not in self.usernames):
            await self.userAlerts(clientSock, json.dumps({"sender":destinationU, "content":"/e", "type":"sys"}))
            return

        await self.send(self.usernames[destinationU], dataSend)

    async def send(self, receiveClient, dataSend:str):    # Prevents Server Crash in case of Lingering Ghost Sockets
        try:        
            await receiveClient.send(dataSend)            
        except websockets.exceptions.ConnectionClosed:
            await self.disconnectionPending.put(receiveClient)

    async def userAlerts(self, clientSock, dataSend:str):    
          
        await clientSock.send(dataSend)    


    async def heartbeats(self):
        while True:            
            for client in self.timeout:
                cTime = time.time() - self.timeout[client]                
                if(cTime >= 40):                    
                    await self.disconnectionPending.put(client)
            
            await asyncio.sleep(25)

    async def Disconnect(self): 
        while True:
            await asyncio.sleep(3)   
            leavingClient = await self.disconnectionPending.get()  
            if(leavingClient):

                dataSend = json.dumps({"sender":self.clients[leavingClient], "content": "/e", "type":"sys"})

                self.usernames.pop(self.clients.pop(leavingClient))                    
                self.timeout.pop(leavingClient)

                await leavingClient.close()

                await self.broadcast('', dataSend, '.') #Empty clientSock as it doesn't exist in self.client.values()


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