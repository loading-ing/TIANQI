from typing import Union
from .inference_engine import InferenceEngine
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()

inference_engine = InferenceEngine()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


class CasualExample(BaseModel):
    content:str
    role:str

@app.post("/casual/chat")
def chat(data:CasualExample):
    return inference_engine.chat(data.content, data.role)