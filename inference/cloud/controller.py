
import json


class ClientController:
    def __init__(self):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        self.config=json.load(open(config_path, "r"))
        self.client_name = self.config["client_name"]
        self.client=self.__create_client()

    def __create_client(self):
        if self.client_name == "deepseek":
            from .client.deepseek_client import DeepseekClient
            clientController = DeepseekClient(base_url=self.config["session"][self.client_name]["base_url"], 
                                    api_key=self.config["session"][self.client_name]["api_key"], 
                                    model=self.config["session"][self.client_name]["model"])
            print("deepseek clientController created")
            return clientController
        else:
            raise ValueError("Invalid client name")
        
        
    def chenge_client(self, client_name):
        self.client_name = client_name
        self.client = self.__create_client()

    def chat(self, content:str, role="user"):
        messages = self.client.pack_message(content, role)
        response = self.client.send_message(messages)
        response = self.client.format_response(response)
        return response
    
if __name__ == "__main__":
    clientController=ClientController()
    content="How to learn English?"
    # response=clientController.chat(content)
    # print(response)
