import json
from .utils.tool import load_config

class Manager:
    def __init__(self):
        self.config=load_config()
        self.example_name=self.config["example_name"]
        self.__create_example()

    
    def __create_example(self):
        for name in self.example_name:
            if name=="casual":
                from .casual.casual import CasualExample
                self.casual_example=CasualExample()
                print("CasualExample created")
            elif name=="rag":
                from .rag.rag import RagExample
                self.rag_example=RagExample()
                print("RagExample created")
            else:
               raise ValueError("Invalid example name")
        
    def casual_chat(self, content:str, role="user"):
        return self.casual_example.chat(content, role)


#  界面调用        
manager=Manager()
        
if __name__=="__main__":
    manager.chat("Hello")