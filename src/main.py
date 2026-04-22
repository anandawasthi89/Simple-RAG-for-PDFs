from fastapi import FastAPI
from src.controller.RAGController import router

app = FastAPI()
app.include_router(router, prefix="/pdf")