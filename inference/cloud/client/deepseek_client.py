
from .base_client import BaseClient
from typing import List, Dict, Any
from openai import OpenAI

class DeepseekClient(BaseClient):
    def __init__(self, base_url: str, api_key: str, model: str):
        super().__init__(base_url, api_key, model)
        self.client=OpenAI(api_key=self.api_key,base_url=self.base_url)


    def send_message(self, messages: List[Dict[str, Any]],stream=False) -> Dict[str, Any]:
        """
        发送对话消息到 Deepseek API。
        """
        response=self.client.chat.completions.create(model=self.model,messages=messages,stream=stream)
        return response

    def pack_message(self, content: str, role="user") -> Dict[str, str]:
        """
        打包 Deepseek API 需要的消息格式。
        """
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": role, "content": content},
        ]
        return messages

    def format_response(self, response: Dict[str, Any]) -> Any:
        """
        格式化 Deepseek API 返回的数据。
        """
        content = response.choices[0].message.content
        return content
    
if __name__ == "__main__":
    import sys
    deepseek_client = DeepseekClient(base_url="https://api.deepseek.com", api_key="sk-5b04419da96f4a1aa7758debfef21fcc", model="deepseek-chat")
    content = "How to learn English?"
    messages = deepseek_client.pack_message(role="user", content=content)
    print(messages)
    response = deepseek_client.send_message(messages)
    print(response)
    print(deepseek_client.format_response(response))
