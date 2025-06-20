import json
from typing import List

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

    def rag_add_texts(self, texts: List[str]) -> None:
        return self.client_controller.rag_add_texts(texts)

    def rag_change_embedding_model(self, new_model_name: str) -> None:
        return self.client_controller.rag_change_embedding_model(new_model_name)

    def rag_delete_by_index(self, index: int) -> None:
        return self.client_controller.rag_delete_by_index(index)
    
    def rag_delete_all(self) -> None:
        return self.client_controller.rag_delete_all()
    
    def rag_similarity_search(self, query: str, k: int = 5) -> List[str]:
        return self.client_controller.rag_similarity_search(query, k)

    def rag_chat(self,query:str,k:int=5)->str:
        """
        进行 RAG 检索增强推理
        :param query: 用户输入的问题
        :param k: 检索 top-k 条上下文
        :return: 大模型推理的回答
        """
        # 1. 检索向量库
        related_docs = self.client_controller.rag_similarity_search(query, k=k)

        # 2. 构建 prompt 模板
        context = "\n\n".join(related_docs)
        prompt = f"""你是一个专业的智能助手。根据以下参考资料，回答用户提出的问题。如果参考资料中没有答案，\
        请礼貌地告诉用户你不知道。\n参考资料： \n{context} \n用户提问：{query} \n你的回答：\n"""

        def event_stream():
            # 发送 context 数据（前端可以监听 type: context）
            yield f"event: context data: {context}\n"

            # 4. 调用大模型生成（逐 token 返回）
            for token in self.client_controller.chat(prompt, role="user"):
                yield f"event: token data: {token}\n"

            # 5. 完成标志
            yield "event: done"
        # 3. 调用大模型推理
        return event_stream()
        

    def get_controller_config(self):
        return self.client_controller.get_config()