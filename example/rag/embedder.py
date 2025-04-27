
from langchain.embeddings import HuggingFaceEmbeddings

class Embedder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.embedder = HuggingFaceEmbeddings(model_name=model_name)

    def get(self):
        return self.embedder