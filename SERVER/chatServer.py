#Header
import json
import time
import asyncio
import websockets

import routing
import message.response_handler as response_handler
from server_state import ServerState

'''
The Server Object
Purpose: The Server. Handles every client's request
Acitivities:
    Starting the Server
    Handling Connection of Clients
    Handling authentication of Clients
    Receiving and Broadcasting Clients' Messages
    Handling Disconenction of Clients
    Handling File storage
'''
class ChatServer:
    '''Initialize'''
    def __init__(self): 
        self.state = ServerState()         
        self.timeout = 40
        self.pingFrequency = 25

        #For testing Purpose it's low, increase in future
        self.fileIOFrequency = 30
        self.disconnectionPending = asyncio.Queue()

    async def start(self) -> None:
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")

            asyncio.create_task(self.Disconnect())
            asyncio.create_task(self.fileHandle())
            asyncio.create_task(self.heartbeats())
            await asyncio.Future()  #while True: but with 0 CPU usage            
        
    async def handleClient(self, clientSock: websockets.ClientConnection) -> None:
        try:
            await asyncio.gather(self.receive(clientSock))
        except websockets.exceptions.ConnectionClosed:
            print("Closed")   


    '''------------------------------------------------'''


    '''Receive and Broadcast Data'''
    async def receive(self, clientSock: websockets.ClientConnection) -> None:
        async for dataReceived in clientSock:   
            response = json.loads(dataReceived)

            '''Payload is json dumped message'''
            destination, payload, self.state = response_handler.parse_response(clientSock, response, self.state)
            
            # Handle Special Cases, otherwise broadcast
            if(destination=='*'):
                match payload:
                    case '/exit': await self.disconnectionPending.put(clientSock)
                    case '/hbp': self.state.timeout[clientSock] = time.time()
                    case '/relog': await self.relog(self.state.uuidsFile[response['content']['username']], clientSock)
                    case '/logged':
                        username = response['content']['username']
                        user_uuid = self.state.uuidsFile[username]
                        await self.broadcast(clientSock, json.dumps({"content":user_uuid, "type": "auth"}), '/s')
                        await self.broadcast(clientSock, json.dumps({"sender":username,"type": "auth" }), '/.')
                continue
            
            await self.broadcast(clientSock, payload, destination)

    async def broadcast(self, clientSock:websockets.ClientConnection, payload:str, destination:str) -> None:
        #Obtain list of Receivers
        receivingClients = routing.parse_destination(clientSock, destination, self.state)

        #Send to receiving clients
        if(receivingClients):
            for client in receivingClients:
                await self.send(client, payload)  
            return
                  
        #If no Receiving Clients but not an Error case
        if(destination.startswith('/r') or destination == '/.'):return
        
        #If receiving client does not exist
        payload = json.dumps({"sender":destination, "content":self.state.codes['user_exit'], "type":"sys"})
        await self.send(clientSock, payload)
       
       
    async def send(self, receiveClient:websockets.ClientConnection, payload:str) -> None:
        try:    
            await receiveClient.send(payload)                      
        except websockets.exceptions.ConnectionClosed:       
            await self.disconnectionPending.put(receiveClient)


    '''------------------------------------------------'''


    '''Disconnection Handling'''
    async def heartbeats(self) -> None:        
        while True:
            cTime = time.time()
            for client in self.state.timeout:
                timeElapsed = cTime - self.state.timeout[client]     
                           
                if(timeElapsed >= self.timeout):    
                    await self.disconnectionPending.put(client)
            await asyncio.sleep(self.pingFrequency)

    async def relog(self, uuid:str, clientSock: websockets.ClientConnection) -> None:
        #So User knows to wait while they Relog
        await self.send(clientSock, json.dumps({"content": self.state.codes['relog_begin'], "type":"sys"}))

        oldClientSock = self.state.uuid_sock[uuid]        
        await self.disconnectionPending.put(oldClientSock)

        #Once Disconnect Finishes
        while oldClientSock not in self.state.sock_uuid:
            await asyncio.sleep(3)

        #Configure Client's new Socket    
        self.state.uuid_sock[uuid] = clientSock
        self.state.sock_uuid[clientSock] = uuid
        self.state.sock_rooms[clientSock] = []

        for room in self.state.accountsFile[uuid]['rooms']:
            self.state.room_socks[room].append(clientSock)
            self.state.sock_rooms[clientSock].append(room)

        # Let user and others know
        username = self.state.accountsFile[uuid]['username']
        await self.broadcast(clientSock, json.dumps({"sender":username, "type": "auth"}), '/.')

        await self.send(clientSock, json.dumps({"content": self.state.codes['relog_finish'], "type": "sys"}))
        return

    async def Disconnect(self) -> None: 
        while True:
            await asyncio.sleep(3)   
            leavingClient = await self.disconnectionPending.get()  
            if(leavingClient):  
                
                #Remove Client from Rooms
                if(leavingClient in self.state.sock_rooms):
                    for room in self.state.sock_rooms[leavingClient]:
                        self.state.room_socks[room].remove(leavingClient)

                    self.state.sock_rooms.pop(leavingClient)
                
                #Room user from Global Variables
                uuid = self.state.sock_uuid.pop(leavingClient)
                self.state.uuid_sock.pop(uuid)

                self.state.timeout.pop(leavingClient)                
                username = self.state.uuid_user(uuid)
                
                #Broadcast others that User is Offline                
                payload = json.dumps({"sender":username, "content": self.state.codes['user_exit'], "type":"sys"})                
                await self.broadcast(leavingClient, payload, '/.')

                await leavingClient.close()


    '''------------------------------------------------'''


    '''Handle File I/O'''
    async def fileHandle(self) -> None:
        while True:   
            
            #Open and store data to each file
            with open("accounts.json", 'w') as accountHandle, open("uuids.json", 'w') as uuidHandle, open("rooms.json", 'w') as roomHandle:
                json.dump(self.state.accountsFile, accountHandle)         
                json.dump(self.state.uuidsFile, uuidHandle)
                json.dump(self.state.roomsFile, roomHandle)

            await asyncio.sleep(self.fileIOFrequency)


'''Entry Point to Event Loop'''
async def eventLoop():
    server = ChatServer()
    await server.start()

#__MAIN__
asyncio.run(eventLoop())