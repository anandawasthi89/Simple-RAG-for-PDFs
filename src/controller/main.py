from fastapi import FastAPI
from src.core.Engine import Engine

app = FastAPI()

engine = None

@app.on_event("startup")
def startup():
    global engine
    engine = Engine()
    engine.process("Resume - Anand Awasthi.pdf")


@app.get("/resolveQuery")
def resolve_query(question: str):
    return {"answer": engine.resolve_query(question)}