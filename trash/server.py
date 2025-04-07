#Server
import asyncio
import websockets

onlineClients = []
async def handleClient(clientSocket):
    onlineClients.append(clientSocket)

    async for message in clientSocket:
        print(f"Received Message: {message}")

        if(message=='exit'):
            await disconnect(clientSocket)
        elif(message=='online'):
            await onlineDisplay(clientSocket)
        
        for client in onlineClients:
            if client != clientSocket:
                await client.send(message)

async def disconnect(sock):
    onlineClients.remove(sock)
    await sock.close(reason='Left')

async def onlineDisplay(sock):
    for client in onlineClients:
        await sock.send(client)


async def main():
    async with websockets.serve(handleClient, "localhost", 8765):
        print("[Server Started!]")
        await asyncio.Future() #Keeps the code running with 0 CPU use

asyncio.run(main())
