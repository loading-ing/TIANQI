from typing import Union
from .inference_engine import InferenceEngine

from fastapi import FastAPI

app = FastAPI()

inference_engine = InferenceEngine()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/chat")
def chat(content: str, role: str = "user"):
    return inference_engine.chat(content, role)