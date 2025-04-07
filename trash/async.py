import asyncio

fileH = open('comm.txt', 'r+')

async def write(usr):
    while True:
        msg = await asyncio.to_thread(input, ">>")
        fileH.write(usr+':  '+ msg)

async def read():
    while True:
        await asyncio.sleep(0.25)
        lastMsg = ""
        content = fileH.read() 

        if(content!= lastMsg):
            print("->", content)
            lastMsg = content


async def main():
    username = input("ENTER USERNAME: ")
    await asyncio.gather(write(username), read())

asyncio.run(main())