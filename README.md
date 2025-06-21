# TIANQI

专属个性化桌面人工智能助手，同时支持私有知识库，娱乐办公两不误。
![](/resources/images/image1.png)
![](/resources/images/image2.png)
![](/resources/images/image3.png)

## 🌟 项目简介
这是一个由人工智能驱动的项目,采用模块化设计，集成以下核心功能：

🎭 智能交互能力：基于大语言模型，提供实时流畅的问答与助手体验。

✨ 私有知识库：支持上传本地资料，构建专属知识库，实现个性化智能问答。

### 🛠️ 快速部署
1. 克隆项目
```shell
git clone https://github.com/loading-ing/TIANQI
cd TIANQI
pip install -r requirements.txt
```
2. 下载大模型
国内推荐[huggingface镜像](https://hf-mirror.com/)
![](/resources/images/download.png)
```shell
# 下载语言模型
huggingface-cli download --resume-download Qwen/Qwen3-0.6B --local-dir Qwen/Qwen3-0.6B

# 下载embedding模型
huggingface-cli download --resume-download BAAI/bge-large-zh-v1.5 --local-dir /BAAI/bge-large-zh-v1.5
```
3. 配置config
修改/inference/local/config.json
```json
{
    "model_name":"Qwen3-0.6B",
    "session":{
        "Qwen3-0.6B":{
            "device":"cuda",
            "model_type":"Casual",
            "model_path":"path/to/Qwen3-0.6B",
            "max_length":4096,
            "temperature":0.7,
            "top_k":50,
            "top_p":0.95
        }
    },
    "rag":"True",
    "rag_settings":{
        "embedding_model_path":"/2023212445/models/BAAI/bge-large-zh-v1.5",
        "device":"cuda",
        "vector_store_path":"/2023212445/projects/TIANQI/resources/rag/db/rag_faiss_store"
    }
}

4. 启动服务
```shell
uvicorn server:app
```

5. 启动程序
```python
python main.py
```

