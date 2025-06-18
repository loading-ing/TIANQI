from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, 
    QScrollArea, QSizePolicy)
from PyQt5.QtGui import QFont

from example.manager import manager
import shutil
import os
import asyncio

class RagPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 文档管理区域
        self.document_manager = DocumentManager()
        layout.addWidget(self.document_manager)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # RAG 对话区域
        self.rag_chat = RagChatArea()
        layout.addWidget(self.rag_chat)


class DocumentManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_files_from_directory()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 拖拽上传区域
        self.upload_area = QLabel("拖拽文件到此上传")
        self.upload_area.setAlignment(Qt.AlignCenter)
        self.upload_area.setFixedHeight(120)
        self.upload_area.setStyleSheet(
            "border: 2px dashed #90CAF9; font-size: 16px; color: #90CAF9;"
        )
        self.upload_area.setAcceptDrops(True)
        self.setAcceptDrops(True)

        layout.addWidget(self.upload_area)

        # 文件列表区域
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["文件名", "大小", "上传时间"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # 按钮区域
        button_layout = QHBoxLayout()
        self.sync_button = QPushButton("同步至向量数据库")
        self.delete_button = QPushButton("删除选中文件")
        
        self.sync_button.clicked.connect(self.sync_to_vectorstore)
        self.delete_button.clicked.connect(self.delete_selected_files)

        button_layout.addWidget(self.sync_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_files_from_directory(self):
        documents_path = manager.rag_example.rag_documents_path
        if not os.path.exists(documents_path):
            os.makedirs(documents_path)
            return

        for file_name in os.listdir(documents_path):
            file_path = os.path.join(documents_path, file_name)
            if os.path.isfile(file_path):
                file_info = QFileInfo(file_path)
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(file_info.fileName()))
                self.table.setItem(row, 1, QTableWidgetItem(str(file_info.size() // 1024) + " KB"))
                self.table.setItem(row, 2, QTableWidgetItem(file_info.lastModified().toString("yyyy-MM-dd HH:mm:ss")))


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.add_file(file_path)

    def add_file(self, file_path):
        # 添加文件到表格
        file_info = QFileInfo(file_path)
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(file_info.fileName()))
        self.table.setItem(row, 1, QTableWidgetItem(str(file_info.size() // 1024) + " KB"))
        self.table.setItem(row, 2, QTableWidgetItem(file_info.lastModified().toString("yyyy-MM-dd HH:mm:ss")))

        # 将文件复制到 manager 的 rag_documents_path
        target_path = os.path.join(manager.rag_example.rag_documents_path, file_info.fileName())
        shutil.copy(file_path, target_path)
    
    def sync_to_vectorstore(self):
        manager.rag_example.upload_document()
    
    def delete_selected_files(self):
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            return

        for row in selected_rows:
            file_name = self.table.item(row.row(), 0).text()
            file_path = os.path.join(manager.rag_example.rag_documents_path, file_name)
            os.remove(file_path)

            self.table.removeRow(row.row())


class RagChatArea(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 历史消息区
        self.chat_area = QVBoxLayout()
        self.chat_area.setAlignment(Qt.AlignTop)

        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.chat_area)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        # 问题输入区
        input_layout = QHBoxLayout()
        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("请输入问题...")
        self.input_box.setFixedHeight(50)
        send_button = QPushButton("发送")
        send_button.setFixedWidth(80)
        send_button.clicked.connect(self.send_question)

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(send_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

    def send_question(self):
        query = self.input_box.toPlainText().strip()
        if not query:
            return

        self.add_message("用户", query, align_right=True)
        self.input_box.clear()

        # 发送到后端（伪代码示例）
        # context_texts = self.search_context(query)
        # final_prompt = self.build_prompt(context_texts, query)
        k=5
        response = self.call_llm(query, k)
        context_texts = response.split("用户提问：")[0].split("参考资料：")[-1]
        answer=response.split("你的回答：")[-1]

        self.add_message("AI", response)

    def add_message(self, sender, message, align_right=False):
        # 复用之前修正好的add_message
        label = QLabel(f"{sender}: {message}")
        label.setWordWrap(True)
        label.setFont(QFont("Arial", 11))
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        label.setMaximumWidth(400)

        label.setStyleSheet(
            "padding: 8px; border-radius: 8px; background-color: #E1F5FE;" if not align_right 
            else "padding: 8px; border-radius: 8px; background-color: #C8E6C9;"
        )

        container = QHBoxLayout()
        container.setAlignment(Qt.AlignRight if align_right else Qt.AlignLeft)
        container.addWidget(label)

        # frame = QFrame()
        # frame.setLayout(container)

        # 在底部spacer前面插入
        # self.chat_area.insertWidget(self.chat_area.count() - 1, frame)
        self.chat_area.addLayout(container)

        # 重要！！滚动到底部
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def search_context(self, query):
        # 向量库搜索伪代码
        return ["文档片段1", "文档片段2"]

    def build_prompt(self, context_texts, query):
        # 简单构建 Prompt
        context = "\n".join(context_texts)
        prompt = f"以下是一些参考资料：\n{context}\n\n基于以上资料回答问题：{query}"
        return prompt

    def call_llm(self, prompt,k=5):
        # 调用本地推理或者API
        response = manager.rag_example.chat(prompt,k)
        return response


