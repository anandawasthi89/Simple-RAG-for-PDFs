from fastapi import FastAPI
from src.controller.RAGController import router
from langchain_core.globals import set_debug

app = FastAPI()
set_debug(True)
app.include_router(router, prefix="/pdf")