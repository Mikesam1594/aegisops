from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import agent

app = FastAPI()


class AskRequest(BaseModel):
    query: str


@app.post("/ask")
def ask(request: AskRequest):
    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": request.query
            }
        ]
    })

    return {
    "answer": response["messages"][-1].content,
    "messages": [
        {
            "type": message.type,
            "content": message.content,
            "tool_calls": getattr(message, "tool_calls", [])
        }
        for message in response["messages"]
    ]
    }