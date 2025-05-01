import asyncio
from apiServer import api_eventLoop
from chatServer import chat_eventLoop

async def main():
    await asyncio.gather(api_eventLoop(), chat_eventLoop())    

asyncio.run(main())