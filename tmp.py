import requests
url = "http://127.0.0.1:8000/" + "rag/chat"
data = {
    "query": "怎么保持健康？",
    "k": 5
}
response = requests.post(url, json=data)
print(response.json())