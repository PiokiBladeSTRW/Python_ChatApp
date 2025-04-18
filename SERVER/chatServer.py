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
        self.pingFrequency = 25

        #For testing Purpose it's low, increase in future
        self.fileIOFrequency = 30
        self.disconnectionPending = asyncio.Queue()

    async def start(self):
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")
            await asyncio.Future()  #while True: but with 0 CPU usage            
        
    async def handleClient(self, clientSock):
        try:
            await asyncio.gather(self.receive(clientSock), self.heartbeats(), self.Disconnect(), self.fileHandle())
        except websockets.exceptions.ConnectionClosed:
            print("Closed")


    '''Receive and Broadcast Data'''
    async def receive(self, clientSock:object):
        async for dataReceived in clientSock:   
            response = json.loads(dataReceived)
            print(response)

            # The user isn't logging in
            if(response['sender']!=''):
                response['sender'] = self.state.accountsFile[response['sender']]['username']

            '''Payload is json dumped message'''
            destination, payload, self.state = message_handler.parse_response(clientSock, response, self.state)
            
            # Handle Special Cases, otherwise broadcast
            if(destination=='*'):
                match payload:
                    case '/exit': await self.disconnectionPending.put(clientSock)
                    case '/hbp': self.state.timeout[clientSock] = time.time()
                    case '/relog': await self.relog(response['content']['username'], clientSock)
                    case '/logged':
                        username = response['content']['username']
                        user_uuid = self.state.uuidsFile[username]
                        await self.broadcast(clientSock, json.dumps({"content":user_uuid, "type": "auth"}), '/s')
                        await self.broadcast(clientSock, json.dumps({"sender":username,"type": "auth" }), '/.')

            else:
                await self.broadcast(clientSock, payload, destination)

    async def broadcast(self, clientSock:object, payload:str, destination:str):
        #Obtain list of Receivers
        receivingClients = routing.parse_destination(clientSock, destination, self.state)

        if(receivingClients):
            for client in receivingClients:
                await self.send(client, payload)  

        else:           
            #If no Receiving Clients but not an Error case
            if(destination.startswith('/r') or destination == '/.'):return
            
            payload = json.dumps({"sender":destination, "content":self.state.codes['user_exit'], "type":"sys"})
            await self.send(clientSock, payload)
       
       
    async def send(self, receiveClient:object, payload:str):   #Prevents Server Crash in case of Lingering Ghost Sockets
        try:    
            await receiveClient.send(payload)                      
        except websockets.exceptions.ConnectionClosed:  
            print("\n>>SEND\n")          
            await self.disconnectionPending.put(receiveClient)


    '''Disconnection Handling'''
    async def relog(self, username, clientSock):

        #So User knows to wait while they Relog
        await self.send(clientSock, json.dumps({"content": self.state.codes['relog_begin'], "type":"sys"}))

        oldClientSock = self.state.user_sock[username]
        print("\n>>RELOG\n")
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
            await asyncio.sleep(self.pingFrequency)

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
                payload = json.dumps({"sender":username, "content": self.state.codes['user_exit'], "type":"sys"})                
                await self.broadcast(leavingClient, payload, '/.')

                await leavingClient.close()

    '''Handle File I/O'''
    async def fileHandle(self):
        while True:   
            print("SAVED")         
            #Accounts.json
            with open("accounts.json", 'w') as fileHandle:
                json.dump(self.state.accountsFile, fileHandle)
            
            with open("uuids.json", 'w') as fileHandle:
                json.dump(self.state.uuidsFile, fileHandle)

            await asyncio.sleep(self.fileIOFrequency)


'''Entry Point to Event Loop'''
async def eventLoop():
    server = ChatServer()
    await server.start()

#__MAIN__
asyncio.run(eventLoop())