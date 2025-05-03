#Header
import json
import time
import asyncio
import websockets

import routing
import message.response_handler as response_handler
from server_state import state

'''
The Server Object
Purpose: The Server. Handles every client's request
Acitivities:
    Starting the Server
    Handling Connection of Clients    
    Receiving and Broadcasting Clients' Messages
    Handling Disconenction of Clients
    Handling File storage
'''
class ChatServer:
    '''Initialize'''
    def __init__(self):        
        self.timeout = 40
        self.pingFrequency = 25

        #For testing Purpose it's low, increase in future
        self.fileIOFrequency = 30
        self.disconnectionPending = asyncio.Queue()

    async def start(self) -> None:
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("CHAT SERVER ACTIVE & LISTENING")

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
            destination, payload = response_handler.parse_response(clientSock, response)
            
            # Handle Special Cases, otherwise broadcast
            if(destination=='*'):
                match payload:
                    case '/exit': await self.disconnectionPending.put(clientSock)
                    case '/hbp': state.timeout[clientSock] = time.time()
                    case '/relog': await self.relog(payload['sender'], clientSock)
                continue
            
            await self.broadcast(clientSock, payload, destination)

    async def broadcast(self, clientSock:websockets.ClientConnection, payload:str, destination:str) -> None:
        #Obtain list of Receivers
        receivingClients = routing.parse_destination(clientSock, destination)

        #Send to receiving clients
        if(receivingClients):
            for client in receivingClients:
                await self.send(client, payload)  
            return
                  
        #If no Receiving Clients but not an Error case
        if(destination.startswith('/r') or destination == '/.'): return
        
        #If receiving client does not exist
        payload = json.dumps({"command":state.system_codes['user_exit'], "content": destination, "type":"sys"})
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
            for client in state.timeout:
                timeElapsed = cTime - state.timeout[client]     
                           
                if(timeElapsed >= self.timeout):    
                    await self.disconnectionPending.put(client)
            await asyncio.sleep(self.pingFrequency)

    async def relog(self, uuid:str, clientSock: websockets.ClientConnection) -> None:
        #So User knows to wait while they Relog
        await self.send(clientSock, json.dumps({"command": state.system_codes['relog_begin'], "type":"sys"}))

        oldClientSock = state.uuid_sock[uuid]        
        await self.disconnectionPending.put(oldClientSock)

        #Once Disconnect Finishes
        while oldClientSock not in state.sock_uuid:
            await asyncio.sleep(3)

        #Configure Client's new Socket    
        state.uuid_sock[uuid] = clientSock
        state.sock_uuid[clientSock] = uuid
        state.sock_rooms[clientSock] = []

        for room in state.accountsFile[uuid]['rooms']:
            state.room_socks[room].append(clientSock)
            state.sock_rooms[clientSock].append(room)

        # Let user and others know
        username = state.accountsFile[uuid]['username']
        await self.broadcast(clientSock, json.dumps({"sender":username, "type": "con"}), '/.')

        await self.send(clientSock, json.dumps({"command": state.system_codes['relog_finish'], "type": "sys"}))
        return

    async def Disconnect(self) -> None: 
        while True:
            await asyncio.sleep(3)   
            leavingClient = await self.disconnectionPending.get()  
            if(leavingClient):  
                
                #Remove Client from Rooms
                if(leavingClient in state.sock_rooms):
                    for room in state.sock_rooms[leavingClient]:
                        state.room_socks[room].remove(leavingClient)

                    state.sock_rooms.pop(leavingClient)
                
                #Room user from Global Variables
                uuid = state.sock_uuid.pop(leavingClient)
                state.uuid_sock.pop(uuid)

                state.timeout.pop(leavingClient)                
                username = state.uuid_user(uuid)
                
                #Broadcast others that User is Offline                
                payload = json.dumps({"command": state.system_codes['user_exit'], "content": [username], "type":"sys"})                
                await self.broadcast(leavingClient, payload, '/.')

                await leavingClient.close()


    '''------------------------------------------------'''


    '''Handle File I/O'''
    async def fileHandle(self) -> None:
        while True:  
            
            #Open and store data to each file
            with open("accounts.json", 'w') as accountHandle, open("uuids.json", 'w') as uuidHandle, open("rooms.json", 'w') as roomHandle:
                json.dump(state.accountsFile, accountHandle)         
                json.dump(state.uuidsFile, uuidHandle)                
                json.dump(state.roomsFile, roomHandle)

            await asyncio.sleep(self.fileIOFrequency)


'''Entry Point to Event Loop'''
async def chat_eventLoop():
    server = ChatServer()
    await server.start()