import auth.auth_handle as auth_handle

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

chatApp = FastAPI()


# Authentication
class authPayload(BaseModel):
    username: str
    password: str
    email: str = ''

@chatApp.post('/login')
def login(credentials: authPayload):
    return auth_handle.login(credentials)    

@chatApp.post('/register')
def register(credentials: authPayload): 
    return auth_handle.register(credentials)

    

#Entry point to server
async def api_eventLoop():    
    config = uvicorn.Config(chatApp, "127.0.0.1", 8000)
    server = uvicorn.Server(config)
    print("API SERVER ACTIVE & LISTENING")
    await server.serve()
    