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
            print(dataRecv)

            decodedData= json.loads(dataRecv)
            match decodedData['type']:
                case 'usr': 
                    print(self.clients)
                    if(decodedData['content']!='%'):
                        self.clients[clientSock].append(decodedData['sender'])
                    try:
                        onlinesMsg = {"sender":"sys[ONLINE LIST]", "content": '\n'.join([x[0] for x in self.clients.values()]), "type": "onl"}                        
                    except IndexError:
                        onlinesMsg = {"sender":"sys[ONLINE LIST]", "content": "No One Online", "type": "onl"}  

                    await self.userAlerts(clientSock, json.dumps(onlinesMsg))



                case 'onl':
                    receiver = next((x for x in self.clients if self.clients[x][0] == decodedData['content']))
                    self.clients[clientSock].append(receiver)

                case _ : pass

            del decodedData
            ''' Check whether the given data is a Special Case or Not '''              

            await self.broadcast(clientSock, dataRecv)

    async def broadcast(self, clientSock, dataRecv:str):
        # for client in self.clients:
        #     if (client != clientSock):
        #         await client.send(dataRecv)
        try:
            receiver = self.clients[clientSock][1]
            await receiver.send(dataRecv)
        except IndexError:      #AKA only one online
            pass
    
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