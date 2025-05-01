from fastapi import FastAPI
from pydantic import BaseModel

authApp = FastAPI()

class authPayload(BaseModel):
    username: str
    password: str

@authApp.post("/login/")
def login(credentials: authPayload):
    if(credentials.username == "Pioki" and credentials.password == "POKI"):
        return {"received": "SUCCESFUL"}
    else:
        return {"received": "FAILURE"}