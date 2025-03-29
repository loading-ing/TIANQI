from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Any

class TransformerClient:
    def __init__(self, model_path: str, device: str = "cpu"):
        """
        初始化 Transformer 客户端。
        :param model_path: 预训练模型的路径或名称。
        :param device: 运行设备 ("cpu" 或 "cuda")
        """
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path).to(self.device)

    def process_prompt(self, prompt: str, max_length: int = 512) -> Dict[str, Any]:
        """
        处理输入提示，转换为模型输入格式。
        :param prompt: 输入的文本提示。
        :param max_length: 生成文本的最大长度。
        :return: 令牌化的输入。
        """
        return self.tokenizer(prompt, return_tensors="pt", max_length=max_length, truncation=True).to(self.device)

    def infer(self, prompt: str, max_length: int = 512, temperature: float = 1.0, top_k: int = 50, top_p: float = 0.95) -> str:
        """
        进行文本推理。
        :param prompt: 输入的文本提示。
        :param max_length: 生成文本的最大长度。
        :param temperature: 控制生成的多样性。
        :param top_k: 采样时考虑的最高概率单词数。
        :param top_p: 采样时的累积概率阈值。
        :return: 生成的文本。
        """
        inputs = self.process_prompt(prompt, max_length)
        output_ids = self.model.generate(
            inputs["input_ids"],
            max_length=max_length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            pad_token_id=self.tokenizer.eos_token_id
        )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)

    def set_device(self, device: str):
        """
        更改运行设备。
        :param device: "cpu" 或 "cuda"
        """
        self.device = device
        self.model.to(self.device)

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型的信息。
        :return: 模型相关信息。
        """
        return {
            "model_name": self.model.config.name_or_path,
            "device": self.device,
            "vocab_size": self.tokenizer.vocab_size
        }

if __name__ == "__main__":
    model_path="/2023212445/models/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
    client=TransformerClient(model_path=model_path,device="cuda")
    prompts="为什么人会感觉到冷?"
    answer=client.infer(prompt=prompts)
    print(answer)