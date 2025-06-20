from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Optional, Union
import faiss
import os
import logging

logging.basicConfig(level=logging.INFO)

class RagClient:
    def __init__(
        self,
        model_name: str = "BAAI/bge-small-zh",
        model_kwargs: dict = {"device": "cuda"},
        encode_kwargs: dict = {"normalize_embeddings": True},
    ):
        """
        本地 RAG 客户端，集成 Embedding 和 Vector Store 基本操作。

        :param model_name: 本地 Huggingface 模型名或路径。
        :param model_kwargs: 模型加载参数。
        :param encode_kwargs: 向量编码参数。
        """
        self.model_name = model_name
        self.model_kwargs = model_kwargs
        self.encode_kwargs = encode_kwargs
        self.embedder = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs=self.model_kwargs,
            encode_kwargs=self.encode_kwargs
        )
        self.vectorstore: Optional[FAISS] = None
        logging.info(f"✅ 成功加载 Embedding 模型：{self.model_name}")

    ## ------------- Embedding 相关 -------------
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        logging.info(f"🔵 正在向量化 {len(texts)} 条文本")
        return self.embedder.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        logging.info(f"🟢 正在向量化查询文本")
        return self.embedder.embed_query(text)

    ## ------------- 向量库管理 -------------
    def create_vectorstore(self, texts: List[str]):
        """
        新建向量库（内存中）。
        """
        logging.info(f"🛠️ 创建新向量库")
        self.vectorstore = FAISS.from_texts(texts, self.embedder)

    def save_vectorstore(self, path: str):
        """
        保存当前向量库到本地。
        """
        if self.vectorstore is None:
            raise ValueError("❌ 当前没有向量库，请先创建。")
        self.vectorstore.save_local(path)
        logging.info(f"✅ 向量库保存成功：{path}")

    def load_vectorstore(self, path: str,allow_dangerous_deserialization=True):
        """
        加载本地向量库。
        """
        if not os.path.exists(path):
            logging.info(f"❌ 指定路径不存在: {path}, 请先创建")
        else:
            self.vectorstore = FAISS.load_local(path, self.embedder,allow_dangerous_deserialization=allow_dangerous_deserialization)
            logging.info(f"✅ 向量库加载成功：{path}")

    ## ------------- 基本操作：增、删、查、改 -------------
    def add_texts(self, texts: List[str]):
        """
        添加新文本到向量库。
        """
        if self.vectorstore is None:
            logging.info("🆕 向量库不存在，自动创建新库")
            self.create_vectorstore(texts)
        else:
            logging.info(f"➕ 向量库添加 {len(texts)} 条数据")
            self.vectorstore.add_texts(texts)

    def similarity_search(self, query: str, k: int = 5):
        """
        相似度查询。
        """
        if self.vectorstore is None:
            raise ValueError("❌ 当前没有加载向量库。")
        logging.info(f"🔍 查询与 \"{query}\" 最相似的 {k} 条记录")
        return self.vectorstore.similarity_search(query, k=k)

    def delete_by_index(self, index: int):
        """
        删除指定索引的数据。
        """
        if self.vectorstore is None:
            raise ValueError("❌ 当前没有加载向量库。")
        logging.info(f"❌ 删除向量库中索引 {index} 的记录")
        id_selector = faiss.IDSelectorBatch([index])
        self.vectorstore.index.remove_ids(id_selector)

    def delete_all(self):
        """
        删除向量库中的所有数据（清空内存中的 FAISS 向量库）。
        """
        logging.info("🧹 正在清空向量库所有数据")
        self.vectorstore = FAISS.from_texts(["创建一个新的向量库"], self.embedder)

    def update_text(self, index: int, new_text: str):
        """
        更新指定索引的数据。
        （实现方式：删除原有 + 插入新文本）
        """
        if self.vectorstore is None:
            raise ValueError("❌ 当前没有加载向量库。")
        logging.info(f"🔄 更新向量库中索引 {index} 的记录")
        self.delete_by_index(index)
        self.add_texts([new_text])

    ## ------------- 其他实用 -------------
    def change_model(self, new_model_name: str):
        """
        动态切换 Embedding 模型。
        """
        logging.info(f"🔄 切换 Embedding 模型到 {new_model_name}")
        self.model_name = new_model_name
        self.embedder = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs=self.model_kwargs,
            encode_kwargs=self.encode_kwargs
        )
        logging.info(f"✅ 模型切换成功")

    def get_vectorstore(self):
        """
        获取当前向量库对象。
        """
        return self.vectorstore

    def get_embedder(self):
        """
        获取当前 embedder 对象。
        """
        return self.embedder


if __name__ == "__main__":
    embeding_model_path = "/2023212445/models/BAAI/bge-large-zh-v1.5"
    vectorstore_path = "/2023212445/projects/TIANQI/resources/rag/db/rag_faiss_store"
    device="cuda"
    rag = RagClient(model_name=embeding_model_path)

    # 向量化 & 保存
    texts = ["你好世界", "今天天气不错", "LangChain 很有趣"]
    health_knowledge = [
    # 营养与饮食
    "均衡饮食应包含五大类食物：谷物、蔬菜、水果、蛋白质和乳制品。成年人每天应摄入300-500克蔬菜，200-350克水果。全谷物应占每日谷物摄入量的1/3以上，它们富含膳食纤维有助于肠道健康。蛋白质来源应多样化，包括鱼、禽、蛋、瘦肉和豆类，每周建议食用鱼类2-3次。",
    
    "成年人每天应饮用1.5-2升水，炎热环境或运动时应增加摄入。最佳饮水方式是少量多次，不要等到口渴才喝水。绿茶和黑咖啡可以计入每日水分摄入，但含糖饮料会增加肥胖和糖尿病风险。观察尿液颜色是简单的水分状态指标，淡黄色表示水分充足。",
    
    # 运动健身
    "世界卫生组织建议成年人每周至少进行150分钟中等强度有氧运动，或75分钟高强度运动。快走、游泳和骑自行车都是优秀的有氧选择。运动应持续10分钟以上才能有效提升心肺功能，最佳运动时间是餐后1-2小时。运动前后要做5-10分钟的热身和放松活动。",
    
    "力量训练每周应进行2-3次，每次训练主要肌群。每组动作8-12次重复，完成2-4组，组间休息30-90秒。正确的姿势比重量更重要，初学者应从自重训练开始。训练后肌肉需要48小时恢复时间，相同肌群不宜连续训练。",
    
    # 睡眠健康
    "成年人每晚需要7-9小时睡眠，最佳入睡时间是晚上10点到11点。卧室温度应保持在18-22℃，完全黑暗环境最利于褪黑素分泌。睡前1小时应避免使用电子设备，蓝光会干扰睡眠周期。建立规律的睡眠时间表，即使在周末也尽量保持一致。",
    
    "短暂失眠时可尝试478呼吸法：吸气4秒，屏息7秒，呼气8秒，重复几次。睡前洗温水澡(40℃左右)有助于降低核心体温促进入睡。日间适度运动和晒太阳有助于调节昼夜节律。长期失眠应就医，避免自行长期服用安眠药物。",
    
    # 心理健康
    "每天10分钟正念冥想可显著降低压力水平。深呼吸练习(腹式呼吸)能激活副交感神经系统。定期运动是天然抗抑郁剂，能促进内啡肽分泌。建立支持性社交网络比独自应对压力更有效。工作时应每90分钟短暂休息，避免持续高压状态。",
    
    "情绪日记可以帮助识别触发因素和反应模式。负面情绪来临时可尝试'5-4-3-2-1'接地技巧：注意5个看到的、4个触摸到的、3个听到的、2个闻到的和1个尝到的事物。艺术表达(绘画、音乐等)是处理复杂情绪的安全途径。当情绪持续低落超过两周应寻求专业帮助。",
    
    # 慢性病预防
    "减少钠盐摄入(每日不超过5克)，增加钾摄入(香蕉、菠菜等)有助于控制血压。定期监测血压(至少每年一次)，正常值为<120/80mmHg。戒烟限酒，酒精每日摄入不应超过25克。保持健康体重(BMI 18.5-23.9)，腰围男性<90cm，女性<85cm。",
    
    "糖尿病患者应监测碳水化合物摄入量，选择低升糖指数食物。每周至少150分钟中等强度运动可提高胰岛素敏感性。定期检查糖化血红蛋白(HbA1c)，理想值应<7%。足部每天检查，预防糖尿病足。每3-6个月进行眼科检查，预防视网膜病变。"
]
    rag.create_vectorstore(health_knowledge)
    rag.save_vectorstore(vectorstore_path)

    # 加载 & 查询
    rag.load_vectorstore(vectorstore_path)
    results = rag.similarity_search("如何保持健康?")
    for doc in results:
        print(doc.page_content)

    # 动态增加新文本
    # rag.add_texts(["RAG 是 Retrieval-Augmented Generation 的缩写"])

    # 删除第一个文档
    # rag.delete_by_index(0)

    # 更新某个文档
    # rag.update_text(index=1, new_text="修改后的新文本")