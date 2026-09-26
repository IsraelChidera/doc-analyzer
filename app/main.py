from fastapi import FastAPI
from app.api.routes import health, execute

app = FastAPI()

app.include_router(health.router)
app.include_router(execute.router)