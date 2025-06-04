from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.user import router as user_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)


@app.get("/")
async def root():
    return {"message": 'Добро пожаловать в API бота для IT-Куба'}

@app.get("/ping")
async def ping():
    return {"ping": "pong"}
