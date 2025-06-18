import requests
import aiohttp
import json
import asyncio

class CasualExample:
    def __init__(self):
        self.config=self.load_config()
        self.base_url = self.config["base_url"]+"casual/"

    def load_config(self):
        import os
        config_path = os.path.join(os.path.dirname(__file__), os.path.pardir)
        config_path = os.path.join(config_path, "config.json")
        config = json.load(open(config_path, "r"))
        return config

    def chat(self, content:str, role="user"):

        url = self.base_url + "chat/"
        data = {
            "content": content,
            "role": role
        }
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(url, json=data) as response:
        #         return await response.json()
        response = requests.post(url, json=data)
        return response.json()


if __name__ == "__main__":
    casualExample = CasualExample()
    content = "怎么学习英语？"
    print(content)
    response = casualExample.chat(content)
    print(response)