import json

class InferenceEngine:
    def __init__(self):
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, "config.json")
        self.config=json.load(open(config_path, "r"))
        self.inference_type = self.config["inference_type"]
        self.client_controller = self.__create_client_controller()
        print("InferenceEngine initialized")

    def __create_client_controller(self):
        if self.inference_type == "local":
            from inference.local.controller import ClientController
            return ClientController()
        elif self.inference_type == "cloud":
            from inference.cloud.controller import ClientController
            return ClientController()
        else:
            raise ValueError("Invalid client type")

    def change_inference_type(self, inference_type):
        self.inference_type = inference_type
        self.client_controller = self.__create_client_controller()

    def chat(self, content:str, role="user"):
        return self.client_controller.chat(content, role)
        