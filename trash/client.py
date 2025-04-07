#Client
import asyncio
import websockets
import encryption as enc

def commands(msg): 
    match msg[:2]:
        case '/e': return 'exit'
        case '/o': return 'online'
        case _: return enc.encryption(f'{username}: {msg}')

async def send(socket):
    while True:
        msg_in= await asyncio.to_thread(input, "->")        

        if(msg_in[0] == "/"):
            msg= commands(msg_in)
        else:
            msg = enc.encryption(f'{username}: {msg_in}')

        await socket.send(msg)

async def receive(socket):
    try:
        async for reply in socket:
            print(enc.decryption(reply))
    except websockets.exceptions.ConnectionClosed:
        print("Offline")
        
async def main():
    async with websockets.connect("ws://localhost:8765") as clientSocket:
        await asyncio.gather(send(clientSocket), receive(clientSocket))

username = input("Enter Username: ")


asyncio.run(main())
