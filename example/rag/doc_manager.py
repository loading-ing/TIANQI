
from langchain.document_loaders import DirectoryLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentLoader:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path

    def load(self):
        """
        加载指定文件夹下的 txt、docx 文件。
        """
        loaders = [
            DirectoryLoader(self.folder_path, glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(self.folder_path, glob="**/*.docx", loader_cls=UnstructuredWordDocumentLoader)
        ]
        docs = []
        for loader in loaders:
            docs.extend(loader.load())
        return docs
    
class TextSplitter:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split(self, documents):
        """
        输入 LangChain 文档对象列表，输出切分后的文档片段。
        """
        return self.splitter.split_documents(documents)