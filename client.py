class chatClient:

    def __init__(self):
        self.clientUsrn = ''
        asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect("ws://localhost:8765") as clientSock:        
            self.clientUsrn = input("\nENTER USERNAME: ")
            await clientSock.send(self.encode("IS ONLINE", "usr"))

            await asyncio.gather(self.send(clientSock), self.receive(clientSock))


    async def send(self,clientSock):
        while True:
            msg = await asyncio.to_thread(input)

            try:
                await clientSock.send(self.encode(msg, 'msg'))

            except websockets.exceptions.ConnectionClosed:
                print("SERVER DOWN") 
                break

    async def receive(self, clientSock):  

        try:
            async for reply in clientSock:  
                            
                response = json.loads(reply)
                match response['type']:
                    case 'msg'|'usr':
                        print(f"{response['sender']}: {response['content']}") 
                    case 'onl':
                        print(f"Onlines: {response['content']}")
                        choiceInput = int(input("->"))
                        choice = self.receiverSelect(response['content'], choiceInput)     
                          

        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN!")

    def encode(self, content, type):
        #Before returning, Content should be encoded
        return json.dumps({"sender": self.clientUsrn, "content": content, "type": type})
    
    async def receiverSelect(self, onlines, choice):
        onlines = onlines.split('\n')
        if(choice < len(onlines)):
            pass
        if(choice == len(onlines)):
           pass
           


#__MAIN__
import asyncio
import websockets
import json
client = chatClient()

'''
Message Format: {"sender": <username>, "content": '--', "type": 'msg/..'}
Types:
->msg: String Message, most common type
->usr: Entry of Username / Retrieval of Online
->onl: Retrieval of Entire Online List
'''