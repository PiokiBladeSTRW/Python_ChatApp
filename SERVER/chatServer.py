class chatServer:

    def __init__(self): 
        self.state = serverState() 
        self.disconnectionPending = asyncio.Queue()

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
                response = json.loads(dataRecv)
                destination, payload, self.state = parser.parse_response(response, self.state, clientSock)

                if(destination=='*'):
                    match payload:
                        case '/e': await self.disconnectionPending.put(clientSock)
                        case '/h': self.state.timeout[clientSock] = time.time()
                else:
                    await self.broadcast(self, clientSock, payload, destination)          


                   

        except websockets.exceptions.ConnectionClosed:
            print("CLOSED")

    async def broadcast(self, clientSock, payload:str, destination:str):        
        receivingClients = broadcaster(clientSock, destination, self.state)

        if(receivingClients==None):
            await self.send(clientSock, json.dumps({"sender":destination, "content":"/e", "type":"sys"}))
            return
        
        for client in receivingClients:
            await self.send(client, payload)

    async def send(self, receiveClient, dataSend:str):    # Prevents Server Crash in case of Lingering Ghost Sockets
        try:        
            await receiveClient.send(dataSend)            
        except websockets.exceptions.ConnectionClosed:
            await self.disconnectionPending.put(receiveClient)

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

import broadcaster
import parser
from state import serverState

server = chatServer()

''' 
Broadcast sends Data to Everyone but Current Client; userAlerts sends only to current Client
Broadcast tells others about user Actions which the user themselves know and need not be notified 
'''