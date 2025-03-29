
import json


class ClientController:
    def __init__(self):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        self.config=json.load(open(config_path, "r"))
        self.model_name = self.config["model_name"]
        self.client=self.__create_client()

    def __create_client(self):
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
        
        
    def chenge_client(self, model_name):
        self.model_name = model_name
        self.client = self.__create_client()

    def chat(self, content:str,role="user"):
        response = self.client.infer(prompt=content,
                                     max_length=self.max_length,
                                     temperature=self.temperature,
                                     top_k=self.top_k,
                                     top_p=self.top_p)
        return response
    
if __name__ == "__main__":
    clientController=ClientController()
    content="How to learn English?"
    response=clientController.chat(content)
    print(response)
