#Client
import asyncio
import websockets

async def send(clientSock):
    while True:
        msg = await asyncio.to_thread(input)
        try:
            await clientSock.send(msg)
        except websockets.exceptions.ConnectionClosed:
            print("SERVER DOWN") 
            break

async def receive(clientSock):
    try:
        async for reply in clientSock:
            print(reply)
    except websockets.exceptions.ConnectionClosed:
        print("SERVER DOWN")


async def main():    
    async with websockets.connect("ws://localhost:8765") as clientSock:        
        usrn = input("\nENTER USERNAME: ")
        await clientSock.send(usrn)

        await asyncio.gather(send(clientSock), receive(clientSock))

asyncio.run(main())