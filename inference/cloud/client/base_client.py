from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseClient(ABC):
    def __init__(self, base_url: str, api_key: str, model: str):
        """
        初始化 API 客户端。
        :param base_url: API 的基础 URL
        :param api_key: 访问 API 的密钥
        :param model: 选择的模型
        """
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.session_params = {}
    
    @abstractmethod
    def send_message(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        发送对话消息。
        :param messages: 对话消息列表
        :return: API 响应
        """
        pass

    @abstractmethod
    def pack_message(self, role: str, content: str) -> Dict[str, str]:
        """
        打包消息。
        :param role: 消息角色 (system, user, assistant)
        :param content: 消息内容
        :return: 结构化的消息字典
        """
        pass

    def update_parameters(self, **kwargs):
        """
        更新 API 调用的参数。
        :param kwargs: 需要更新的参数
        """
        self.session_params.update(kwargs)
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        获取当前会话的参数。
        :return: 参数字典
        """
        return self.session_params

    @abstractmethod
    def format_response(self, response: Dict[str, Any]) -> Any:
        """
        格式化 API 返回的结果。
        :param response: API 原始返回数据
        :return: 格式化的内容
        """
        pass
