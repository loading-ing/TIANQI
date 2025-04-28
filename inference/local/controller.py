
import json
from typing import List


class ClientController:
    def __init__(self):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        self.config=json.load(open(config_path, "r"))
        self.model_name = self.config["model_name"]
        self.transformer_client=self.__create_transformer_client()
        self.rag_client=self.__create_rag_client()

    def __create_transformer_client(self):
        self.model_type = self.config["session"][self.model_name]["model_type"]
        if self.model_type == "Casual":
            from .client.transformer_client import TransformerClient
            self.device=self.config["session"][self.model_name]["device"]
            self.model_path=self.config["session"][self.model_name]["model_path"]
            self.max_length=self.config["session"][self.model_name]["max_length"]
            self.temperature=self.config["session"][self.model_name]["temperature"]
            self.top_k=self.config["session"][self.model_name]["top_k"]
            self.top_p=self.config["session"][self.model_name]["top_p"]
            clientController = TransformerClient(model_path=self.model_path,
                                                 device=self.device)
            print(self.model_name,"clientController created")
            return clientController
        else:
            raise ValueError("Invalid client name")

    def __create_rag_client(self):
        if self.config["rag"]=="True":
            from .client.rag_client import RagClient
            self.embedding_model_path = self.config["rag_settings"]["embedding_model_path"]
            self.embedding_model_device = self.config["rag_settings"]["device"]
            self.vector_store_path = self.config["rag_settings"]["vector_store_path"]
            rag_client = RagClient(model_name=self.embedding_model_path,
                                 model_kwargs={"device": self.embedding_model_device})
            rag_client.load_vectorstore(path=self.vector_store_path)
            print("rag_client created")
            return rag_client
        else:
            return None

    def activate_rag(self):
        self.config["rag"]==True
        self.rag_client = self.__create_rag_client()

    def deactivate_rag(self):
        self.config["rag"]==False
        self.rag_client = None
        
        
    def chenge_client(self, model_name):
        self.model_name = model_name
        self.transformer_client = self.__create_client()

    def chat(self, content:str,role="user"):
        response = self.transformer_client.infer(prompt=content,
                                     max_length=self.max_length,
                                     temperature=self.temperature,
                                     top_k=self.top_k,
                                     top_p=self.top_p)
        return response

    def rag_add_texts(self, texts: List[str]) -> None:
        if self.rag_client is not None:
            self.rag_client.add_texts(texts)
            self.rag_client.save_vectorstore(self.vector_store_path)
        else:
            raise ValueError("Rag is not activated")

    def rag_similarity_search(self, query: str, k: int = 5) -> List[str]:
        if self.rag_client is not None:
            results = self.rag_client.similarity_search(query, k)
            return [doc.page_content for doc in results]
        else:
            raise ValueError("Rag is not activated")

    def rag_delete_by_index(self, index: int) -> None:
        if self.rag_client is not None:
            self.rag_client.delete_by_index(index)
            self.rag_client.save_vectorstore(self.vector_store_path)
        else:
            raise ValueError("Rag is not activated")

    def rag_update_text(self, index: int, new_text: str) -> None:
        if self.rag_client is not None:
            self.rag_client.update_text(index, new_text)
            self.rag_client.save_vectorstore(self.vector_store_path)
        else:
            raise ValueError("Rag is not activated")

    def rag_change_embedding_model(self, new_model_name: str) -> None:
        if self.rag_client is not None:
            self.rag_client.change_model(new_model_name)
            self.rag_client.save_vectorstore(self.vector_store_path)
        else:
            raise ValueError("Rag is not activated")
    
if __name__ == "__main__":
    clientController=ClientController()
    content="How to learn English?"
    response=clientController.chat(content)
    print(response)
