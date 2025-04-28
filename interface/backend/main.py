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

@app.post("/casual/chat/")
def chat(data:CasualExample):
    return inference_engine.chat(data.content, data.role)

class TextsRequest(BaseModel):
    texts: list[str]

@app.post("/rag/add_texts/")
def rag_add_texts(data: TextsRequest):
    inference_engine.rag_add_texts(data.texts)
    return {"status": "success"}


class IndexRequest(BaseModel):
    index: int

@app.post("/rag/delete_by_index/")
def rag_delete_by_index(data: IndexRequest):
    inference_engine.rag_delete_by_index(data.index)
    return {"status": "success"}

class ChangeEmbeddingModelRequest(BaseModel):
    new_model_name: str
@app.post("/rag/change_embedding_model/")
def rag_change_embedding_model(data:ChangeEmbeddingModelRequest):
    inference_engine.rag_change_embedding_model(data.new_model_name)
    return {"status": "success"}


class UpdateTextRequest(BaseModel):
    index: int
    new_text: str

@app.post("/rag/update_text/")
def rag_update_text(data: UpdateTextRequest):
    inference_engine.rag_update_text(data.index, data.new_text)
    return {"status": "success"}

class ChatRequest(BaseModel):
    query: str
    k: int = 5

@app.post("/rag/chat/")
def rag_chat(data: ChatRequest):
    return inference_engine.rag_chat(data.query, data.k)