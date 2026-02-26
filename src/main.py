from fastapi import FastAPI
from pydantic import BaseModel
from src.agent.agents import run_agent
from src.api.family import router as family_router

app = FastAPI(
    title="Family Tree AI",
    description="Tool-calling AI over FalkorDB Knowledge Graph",
    version="1.0"
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    graph: dict | None = None


@app.get("/")
def health_check():
    return {"status": "API is running"}


@app.post("/ask", response_model=QueryResponse)
def ask_question(request: QueryRequest):
    result = run_agent(request.question)
    return result



app.include_router(family_router)