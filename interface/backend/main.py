from typing import Union
from .inference_engine import InferenceEngine
from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio

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
    return StreamingResponse(inference_engine.chat(data.content, data.role),media_type="text/event-stream")

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

@app.post("/rag/delete_all/")
def rag_delete_all():
    inference_engine.rag_delete_all()
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
    return StreamingResponse(inference_engine.rag_chat(data.query, data.k),media_type="text/event-stream")


@app.post("/config/")
def get_config():
    return inference_engine.get_controller_config()

@app.get("/stream")
async def stream_output(prompt: str):
    async def event_generator():
        reversed_text = prompt[::-1]
        for ch in reversed_text:
            await asyncio.sleep(0.1)  # 模拟生成速度
            yield f"data: {ch}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")