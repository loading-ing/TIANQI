
from langchain_community.document_loaders import DirectoryLoader, TextLoader, UnstructuredWordDocumentLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentLoader:
    def __init__(self, folder_path: str=None):
        self.folder_path = folder_path

    def load(self,file_path: str):
        """
        加载指定文件夹下的 txt、docx 文件。
        """
        if  file_path is None:
            file_path = self.folder_path
        loaders = [
            DirectoryLoader(file_path, glob="**/*.txt", loader_cls=TextLoader),
            DirectoryLoader(file_path, glob="**/*.docx", loader_cls=UnstructuredWordDocumentLoader),
            DirectoryLoader(file_path, glob="**/*.pdf", loader_cls=UnstructuredPDFLoader)
        ]
        docs = []
        for loader in loaders:
            docs.extend(loader.load())
        # print(docs)
        return docs
    
class TextSplitter:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split_texts(self, documents):
        """
        输入 LangChain 文档对象列表，输出切分后的文档片段。
        """
        # docs=[Document(page_content=txt) for txt in documents]
        return self.splitter.split_documents(documents=documents)