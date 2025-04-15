class chatServer:
    '''Initialize'''
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


    '''Receive and Broadcast Data'''
    async def receive(self, clientSock):
        try:
            async for dataRecv in clientSock:   
                response = json.loads(dataRecv)

                '''Payload is json dumped message'''
                destination, payload, self.state = parser.parse_response(clientSock, response, self.state)
                
                # Handle Special Cases, otherwise broadcast
                if(destination=='*'):
                    match payload:
                        case '/e': await self.disconnectionPending.put(clientSock)
                        case '/h': self.state.timeout[clientSock] = time.time()
                else:
                    await self.broadcast(clientSock, payload, destination)

        except websockets.exceptions.ConnectionClosed:
            print("CLOSED")


    async def broadcast(self, clientSock, payload:str, destination:str):
        receivingClients = broadcaster.parse_destination(clientSock, destination, self.state)

        if(receivingClients):
            for client in receivingClients:
                await self.send(client, payload)                
        else:
            #If Hollow Room or just one User, to avoid Buggy Rooms and './' Offline messages
            if(destination.startswith('/r') or len(self.state.sock_user)==1): return

            payload = json.dumps({"sender":destination, "content":"/e", "type":"sys"})
            await self.send(clientSock, payload)
       
    async def send(self, receiveClient, payload:str):   #Prevents Server Crash in case of Lingering Ghost Sockets
        try:        
            await receiveClient.send(payload)            
        except websockets.exceptions.ConnectionClosed:
            await self.disconnectionPending.put(receiveClient)


    '''Disconnection Handling'''
    async def heartbeats(self):
        while True:            
            for client in self.state.timeout:
                cTime = time.time() - self.state.timeout[client]                
                if(cTime >= 40):                    
                    await self.disconnectionPending.put(client)
            await asyncio.sleep(25)

    async def Disconnect(self): 
        while True:
            await asyncio.sleep(3)   
            leavingClient = await self.disconnectionPending.get()  
            if(leavingClient):

                payload = json.dumps({"sender":self.state.sock_user[leavingClient], "content": "/e", "type":"sys"})                
                await self.broadcast(leavingClient, payload, '.')

                self.state.user_sock.pop(self.state.sock_user.pop(leavingClient))
                self.state.timeout.pop(leavingClient)

                await leavingClient.close()
                

#Run
import asyncio
import websockets
import json
import time

import broadcaster
import parser
from state import serverState

server = chatServer()