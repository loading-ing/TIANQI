# vectorstores/faiss_store.py

from langchain.vectorstores import FAISS

class VectorStore:
    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.store = None

    def build(self, documents):
        self.store = FAISS.from_documents(documents, self.embedding_model)

    def save(self, folder_path: str):
        if self.store is not None:
            self.store.save_local(folder_path)

    @classmethod
    def load(cls, folder_path: str, embedding_model):
        store = FAISS.load_local(folder_path, embedding_model)
        instance = cls(embedding_model)
        instance.store = store
        return instance

    def search(self, query: str, top_k=5):
        return self.store.similarity_search(query, k=top_k)
