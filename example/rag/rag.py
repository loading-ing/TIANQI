import requests
import json
from .doc_manager import DocumentLoader, TextSplitter
from ..utils.tool import load_config
from typing import List
import aiohttp
import asyncio


class RagExample:
    def __init__(self):
        self.config = load_config()
        self.base_url = self.config["base_url"].rstrip("/") + "/rag/"
        self.document_loader = DocumentLoader(self.config["rag_documents_path"])
        self.text_splitter = TextSplitter()
        self.rag_documents_path = self.config["rag_documents_path"]

    def chat(self, query: str, k: int = 5):
        url = self.base_url + "chat/"
        data = {
            "query": query,
            "k": k
        }
        response = requests.post(url, json=data)
        return response.json()

    async def chat_stream(self, query: str, k: int = 5):
        """异步流式输出"""
        url = self.base_url + "chat/"
        data = {
            "query": query,
            "k": k
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url,json=data) as resp:
                    if resp.status != 200:
                        yield f"HTTP error {resp.status}"
                        return
                    async for line in resp.content:
                        yield line.decode("utf-8",errors="ignore").strip()
                        # yield line
        except Exception as e:
            yield f"event: token Error: {str(e)}"

    def upload_document(self, filepath: str=None):
        """
        加载本地文档，分割成小段，上传到服务器更新向量库
        """
        if filepath is None:
            filepath = self.rag_documents_path
        # 加载文本
        texts = self.document_loader.load(filepath)
        # 分割文本
        chunks = self.text_splitter.split_texts(texts)
        chunks = [chunk.page_content.strip() for chunk in chunks]

        # 上传每一段
        url = self.base_url + "add_texts/"
        data = {"texts": chunks}
        response = requests.post(url, json=data)
        return response.json()

    def upload_texts(self, texts: List[str]):
        """
        直接上传一批文本，不经过文档读取
        """
        url = self.base_url + "add_texts/"
        data = {"texts": texts}
        response = requests.post(url, json=data)
        return response.json()

    def delete_by_index(self, index: int):
        """
        根据索引删除向量库中的一条记录
        """
        url = self.base_url + "delete_by_index/"
        data = {"index": index}
        response = requests.post(url, json=data)
        return response.json()

    def delete_vectorstore_all(self):
        """
        删除向量库的所有记录
        """
        url = self.base_url + "delete_all/"
        response = requests.post(url)
        return response.json()

    def search_similar(self, query: str, k: int = 5):
        """
        只做检索，不做推理
        """
        url = self.base_url + "search/"
        data = {
            "query": query,
            "k": k
        }
        response = requests.post(url, json=data)
        return response.json()

    def change_embedding_model(self, model_name: str):
        """
        切换服务器端使用的 Embedding 模型
        """
        url = self.base_url + "change_embedding_model/"
        data = {
            "model_name": model_name
        }
        response = requests.post(url, json=data)
        return response.json()



if __name__ == "__main__":
    ragExample = RagExample()
    content = "怎么学习英语？"
    print(content)
    response = ragExample.chat(content)
    print(response)