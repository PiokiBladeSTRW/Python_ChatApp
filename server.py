class chatServer:

    def __init__(self):
        self.clients = {}
        asyncio.run(self.start())  
        

    async def start(self):
        async with websockets.serve(self.handleClient, "localhost", 8765):
            print("SERVER ON")
            await asyncio.Future()  #while True: but with 0 CPU usage
        
    async def handleClient(self, clientSock):
        self.clients[clientSock]= []

        await self.receive(clientSock)


    async def receive(self, clientSock):
        async for dataRecv in clientSock:
            #print(dataRecv)

            ''' Check whether the given data is a Special Case or Not
                Type 'usr': Client just connected to Server, is yet to Properly Establish Connection
                Type 'onl': Client is finalizing connection to Server
            '''     

            decodedData= json.loads(dataRecv)
            match decodedData['type']:
                case 'usr': 
                    
                    if(decodedData['content']!='%'):
                        self.clients[clientSock].append(decodedData['sender'])
                    
                    if(len(self.clients)==1):
                        onlinesMsg = {"sender":"sys[ONLINE LIST]", "content": "No One Online", "type": "onl"} 
                    else:
                        content = '\n'.join([x[0] for x in self.clients.values() if x[0] != self.clients[clientSock][0]])
                        onlinesMsg = {"sender":"sys[ONLINE LIST]", "content": content, "type": "onl"}                        

                    await self.userAlerts(clientSock, json.dumps(onlinesMsg))
                    dataRecv= ''

                case 'onl':
                    receiver = next((x for x in self.clients if self.clients[x][0] == decodedData['content']))
                    self.clients[clientSock].append(receiver)
                    dataRecv= ''

                case _ : pass

            del decodedData
                  
            await self.broadcast(clientSock, dataRecv)


    async def broadcast(self, clientSock, dataRecv:str):
        # for client in self.clients:
        #     if (client != clientSock):
        #         await client.send(dataRecv)
        if(dataRecv==''):           #Only one online
            return
 
        receiver = self.clients[clientSock][1]
        await receiver.send(dataRecv)

    
    async def userAlerts(self, clientSock, msg):
        await clientSock.send(msg)

    ''' 
    Broadcast sends Data to Everyone but Current Client; userAlerts sends only to current Client
    Broadcast tells others about user Actions which the user themselves know and need not be notified 
    '''

#Run
import asyncio
import websockets
import json
server = chatServer()