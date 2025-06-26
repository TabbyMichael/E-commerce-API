from fastapi import FastAPI

from ecommerce_api.routes import users

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/")
async def root():
    return {"message": "Welcome to the E-commerce API"}