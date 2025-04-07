#Server
import asyncio
import websockets

clients= []

async def handleClient(clientSock):
    clients.append(clientSock)
    await receive(clientSock)

async def receive(clientSock):    
    async for message in clientSock:
        print(message)
        await broadcast(clientSock, message)

async def broadcast(clientSock, msg):
    for client in clients:
        if (client!=clientSock):
            await client.send(msg)


async def main():
    async with websockets.serve(handleClient, "localhost", 8765):
        print("SERVER ON")
        await asyncio.Future()

asyncio.run(main())