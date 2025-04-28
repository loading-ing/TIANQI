import requests
import json
from document_manager import DocumentLoader, TextSplitter
from ..utils.tool import load_config

class RagExample:
    def __init__(self):
        self.config=self.load_config()
        self.base_url = self.config["base_url"]+"rag/"
        self.document_loader = DocumentLoader(self.config["rag_doucument_path"])
        self.text_splitter = TextSplitter()

    def chat(self, query:str, k:int=5):
        url = self.base_url + "chat/"
        data = {
            "query": content,
            "k": k
        }
        response = requests.post(url, json=data)
        return response.json()


if __name__ == "__main__":
    ragExample = RagExample()
    content = "怎么学习英语？"
    print(content)
    response = ragExample.chat(content)
    print(response)