class chatClient:

    def __init__(self):
        self.clientUsrn = ''
        self.receiver = ''
        self.pReceiver = ''
        self.clientSock = None
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSocket:   
            self.clientSock = clientSocket 

            self.clientUsrn = input("\nENTER USERNAME: ").strip()
            await self.send("", "usr")

            try:
                await asyncio.gather(self.message(), self.receive(),self.heartbeat())
            except asyncio.exceptions.CancelledError:       # i.e., tasks have been cancelled, program exit
                pass


    async def receive(self):
        try:
            async for response in self.clientSock:                  
                response = json.loads(response)                                          

                if(response['type'] == 'msg'):
                    if(response['sender'] == self.receiver):
                        print(f"> {response['content']}\n")                         
                        continue

                    if(response['sender'].startswith('[')): #AKA Room Message, and Room messages are only sent to Members
                        print(f"{response['sender']}: {response['content']}\n")
                        continue

                    print(f"< {response['sender']}: {response['content']} >")   # Outsider Message

                elif(response['type'] == 'usr'):
                    print(f"[{response['sender']} is ONLINE]") 
                
                elif(response['type'] == 'sys'):        

                    #If Else to allow System to Manipulate Clients
                    if(response['content'] == '/e'):
                        print(f"[{response['sender']} is OFFLINE]")
                        if(self.receiver == response['sender']): self.receiver = ''
                    else:
                        print(f"{{System}}: {response['content']}")
                
                print()

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")
            await self.disconnect()

    async def message(self):
        while True:
            msg = await asyncio.to_thread(input)

            '''Check for Command
            [If parsed, that implies the command is receied by Server (type:sys)]

            /dm <username> <msg>    : Initiates a DM with given Username as Receiver
            /#                      : Removes Receiver, that is closing a DM
            /exit                   : Exit                                            [Parsed as /e]
            /online                 : Online List                                     [Parsed as /o]        
            /create <room>          : Create a Room                                   [Parsed as /c+<room>]
            /join <room> <msg>      : Initiates messaging with Room as Receiver        
            /rooms                  : List of Rooms                                   [Parsed as /r]
            /b                      : Backtracks Receiver to Swap
            '''
                       
            if(msg.startswith('/dm')):         
                data = msg.split()
                self.receiverChange(data[1])

                msg = ' '.join(data[2::])
                await self.send(msg, 'msg')
            
            elif(msg.startswith('/join')):
                data = msg.split()
                self.receiverChange('/r'+data[1])

                msg= ' '.join(data[2::])
                await self.send(msg, 'msg')

            elif(msg.startswith('/#')): 
                self.receiverChange('')
            
            elif(msg.startswith('/b')):
                self.receiver, self.pReceiver = self.pReceiver, self.receiver                

            elif(msg.startswith('/create')):
                data = msg.split()
                self.receiverChange('/r'+data[1])
                
                msg = '/c'+data[1]
                await self.send(msg, 'sys')

            elif(msg.startswith('/exit')):      
                await self.send('/e', 'sys')
                await self.disconnect()
                
            elif(msg.startswith('/online')):
                await self.send('/o', 'sys')

            elif(msg.startswith('/rooms')):
                await self.send('/r', 'sys')

            else:                              
                if(self.receiver):
                    await self.send(msg, 'msg')
                else:
                    print("[!!ERROR: No Destination Chosen]")   

            print()             

    async def send(self, content, type):
        try:
            await self.clientSock.send(self.encode(content, type))

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN") 
            await self.disconnect()


    async def heartbeat(self):
        while True:
            await self.send('', 'hbp')
            await asyncio.sleep(20)
    
    async def disconnect(self):
        await self.clientSock.close()
        for task in asyncio.all_tasks():
            task.cancel()
            return
        

    def receiverChange(self, receiver):
        self.pReceiver = self.receiver
        self.receiver = receiver

        if(receiver==''): receiver = 'No One'
        
        if(receiver.startswith('/r')):
            print('', "="*25, f"Now Chatting in {receiver[2::]}", "="*25, sep='\n')
            return
    
        print('', "="*25, f"Now Chatting with {receiver}", "="*25, sep='\n')


    def encode(self, content, type):
        '''
        Types:
        ->msg: Default String Message
        ->usr: Entry of Username / Retrieval of '<> IS ONLINE'
        ->sys: System Message / Commands
        ->hbp: Heartbeat Pings. Letting Server know you are there.
        '''
        timestamp = time.strftime("%H:%M", time.localtime())

        data = {"sender": self.clientUsrn, 
                "receiver": self.receiver, 
                "content": content, ""
                "type": type,
                "timestamp": timestamp}
        
        if(type in ('usr', 'sys', 'hbp')):
            data.pop('receiver')

        return json.dumps(data)
        
#__MAIN__
import asyncio
import websockets
import json
import time
client = chatClient()
'''
Message Format: {"sender": <username>, 
                "receiver": <username>, 
                "content": '--', 
                "type": 'msg/..',}
        
'''