#Header
import json
import time
import asyncio
import websockets

import routing
import message_handler 
from server_state import ServerState


'''Main Class handling Server'''
class ChatServer:
    '''Initialize'''
    def __init__(self): 
        self.state = ServerState() 
        self.timeout = 40
        self.pignFrequency = 25
        self.disconnectionPending = asyncio.Queue()

    async def start(self):
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")
            await asyncio.Future()  #while True: but with 0 CPU usage            
        
    async def handleClient(self, clientSock):
        await asyncio.gather(self.receive(clientSock), self.heartbeats(), self.Disconnect())


    '''Receive and Broadcast Data'''
    async def receive(self, clientSock:object):
        try:
            async for dataReceived in clientSock:   
                response = json.loads(dataReceived)               

                '''Payload is json dumped message'''
                destination, payload, self.state = message_handler.parse_response(clientSock, response, self.state)
                
                # Handle Special Cases, otherwise broadcast
                if(destination=='*'):
                    match payload:
                        case '/exit': await self.disconnectionPending.put(clientSock)
                        case '/hbp': self.state.timeout[clientSock] = time.time()
                        case '/relog': await self.relog(response['sender'], clientSock)
                        case '/logged':
                            username = response['content']['username']
                            await self.broadcast(clientSock, json.dumps({"content":True, "type": "auth"}), '/s')
                            await self.broadcast(clientSock, json.dumps({"sender":username,"type": "auth" }), '/.')

                else:
                    await self.broadcast(clientSock, payload, destination)
        except websockets.exceptions.ConnectionClosed:
            print("CLOSED")

    async def broadcast(self, clientSock:object, payload:str, destination:str):
        receivingClients = routing.parse_destination(clientSock, destination, self.state)

        if(receivingClients):
            for client in receivingClients:
                await self.send(client, payload)  

        else:            
            #If Hollow Room or just one User, to avoid Buggy Rooms and './' Offline messages
            if(destination.startswith('/r') or len(self.state.sock_user)==1): return

            payload = json.dumps({"sender":destination, "content":self.state.codes['user_exit'], "type":"sys"})
            await self.send(clientSock, payload)
       
    async def send(self, receiveClient:object, payload:str):   #Prevents Server Crash in case of Lingering Ghost Sockets
        try:        
            await receiveClient.send(payload)            
        except websockets.exceptions.ConnectionClosed:            
            await self.disconnectionPending.put(receiveClient)


    '''Disconnection Handling'''
    async def relog(self, username, clientSock):

        #So User knows to wait while they Relog
        await self.send(clientSock, json.dumps({"content": self.state.codes['relog_begin'], "type":"sys"}))

        oldClientSock = self.state.user_sock[username]
        await self.disconnectionPending.put(oldClientSock)

        #Once Disconnect Finishes
        while True:
            await asyncio.sleep(3)
            if(oldClientSock not in self.state.sock_user):
                self.state.user_sock[username] = clientSock
                self.state.sock_user[clientSock] = username
                await self.broadcast(clientSock, json.dumps({"sender":username, "type": "auth"}), '/.')

                await self.send(clientSock, json.dumps({"content": self.state.codes['relog_finish'], "type": "sys"}))
                return

    async def heartbeats(self):
        while True:            
            for client in self.state.timeout:
                cTime = time.time() - self.state.timeout[client]                
                if(cTime >= self.timeout):    
                    await self.disconnectionPending.put(client)
            await asyncio.sleep(self.pignFrequency)

    async def Disconnect(self): 
        while True:
            await asyncio.sleep(3)   
            leavingClient = await self.disconnectionPending.get()  
            if(leavingClient):  
                
                #Remove All Reference of Client
                if(leavingClient in self.state.sock_room):
                    clientRoom = self.state.sock_room.pop(leavingClient)
                    self.state.rooms[clientRoom].remove(leavingClient)

                username = self.state.sock_user.pop(leavingClient)       
                self.state.user_sock.pop(username)
                self.state.timeout.pop(leavingClient)

                #Broadcast others that User is Offline                
                payload = json.dumps({"sender":self.state.sock_user[leavingClient], "content": self.state.codes['user_exit'], "type":"sys"})                
                await self.broadcast(leavingClient, payload, '/.')

                await leavingClient.close()

'''Entry Point to Event Loop'''
async def eventLoop():
    server = ChatServer()
    await server.start()

#__MAIN__
asyncio.run(eventLoop())