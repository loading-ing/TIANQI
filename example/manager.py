import json
from .utils.tool import load_config

class Manager:
    def __init__(self):
        self.config=load_config()
        self.example_name=self.config["example_name"]
        self.example=self.__create_example()

    
    def __create_example(self):
        if self.example_name=="casual":
            from .casual.casual import CasualExample
            example=CasualExample()
            print("CasualExample created")
            return example
        else:
            raise ValueError("Invalid example name")
        
    def chat(self, content:str, role="user"):
        if self.example_name=="casual":
            return self.example.chat(content, role)
        else:
            raise ValueError("Invalid example name")
        
if __name__=="__main__":
    manager=Manager()
    manager.chat("Hello")