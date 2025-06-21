from re import L
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QTextEdit, QPushButton, QLineEdit, QComboBox, QListWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QFrame, QFileDialog, QMessageBox, QTabWidget, QCheckBox, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
import random
import os
import shutil
import asyncio

from example.manager import manager

class RagPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.init_mock_data()
        
    def setup_ui(self):
        """设置UI界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("Retrieval-Augmented Generation (RAG)")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding-bottom: 10px; border-bottom: 2px solid #3498db;")
        main_layout.addWidget(title_label)
        
        # 创建中心区域
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧面板：文档管理和设置
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # 状态栏
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d;")

        # 文档管理部分
        doc_group = self.create_document_group()
        left_layout.addWidget(doc_group)
        
        # 设置部分
        settings_group = self.create_settings_group()
        left_layout.addWidget(settings_group)

        
        # 右侧面板：查询和结果
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # 查询输入区域
        query_group = self.create_query_group()
        right_layout.addWidget(query_group)
        
        # 结果展示区域
        results_tabs = self.create_results_tabs()
        right_layout.addWidget(results_tabs)
        
        # 添加到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter, 1)  # 1表示使用所有可用空间
        
        # 状态栏
        self.status_bar = QWidget()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(5, 5, 5, 5)
        
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(self.status_bar)
        
        # 设置样式
        self.setStyleSheet("""
            RagPage {
                background-color: #f5f7fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                color: #2c3e50;
            }
            QListWidget, QTableWidget, QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QTableWidget {
                gridline-color: #eee;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 6px;
                border: none;
                font-weight: bold;
                color: #2c3e50;
            }
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
            }
            QPushButton:hover {
                background-color: #d6dbdf;
            }
            #queryButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: 1px solid #2980b9;
            }
            #queryButton:hover {
                background-color: #2980b9;
            }
            #uploadButton, #deleteButton {
                background-color: #2ecc71;
                color: white;
                border: 1px solid #27ae60;
            }
            #uploadButton:hover, #deleteButton:hover {
                background-color: #27ae60;
            }
            #deleteButton {
                background-color: #e74c3c;
                border: 1px solid #c0392b;
            }
            #deleteButton:hover {
                background-color: #c0392b;
            }
        """)
    
    def create_document_group(self):
        """创建文档管理组"""
        group = QGroupBox("Document Management")
        layout = QVBoxLayout(group)
        
        # 文档操作按钮
        btn_layout = QHBoxLayout()
        self.upload_btn = QPushButton("Upload Documents")
        self.upload_btn.setObjectName("uploadButton")
        self.upload_btn.setIcon(QIcon.fromTheme("document-open"))
        self.upload_btn.clicked.connect(self.upload_documents)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.clicked.connect(self.delete_document)
        self.delete_btn.setEnabled(False)

        self.reload_btn = QPushButton("Reload to Vectorstore")
        self.reload_btn.setObjectName("reloadButton")
        self.reload_btn.setIcon(QIcon.fromTheme("document-open"))
        self.reload_btn.clicked.connect(self.reload_to_vectorstore)
        
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.reload_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 文档列表
        self.doc_list = QListWidget()
        self.doc_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.doc_list.itemSelectionChanged.connect(self.toggle_delete_button)
        layout.addWidget(self.doc_list)
        
        return group
    
    def create_settings_group(self):
        """创建设置组"""
        group = QGroupBox("RAG Configuration")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        

        try:
            self.model_config=manager.get_model_config()
            # print(self.model_config)
        except:
            self.model_config=None
            self.status_label.setText("server not connected")

        # 模型选择
        if self.model_config:
            model_names=[key for key in self.model_config["session"]]
        else:
            model_names=["no model"]

        
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("LLM Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(model_names)
        self.model_combo.setCurrentIndex(0)
        model_layout.addWidget(self.model_combo, 1)
        
        # 检索设置
        retrieval_layout = QHBoxLayout()
        retrieval_layout.addWidget(QLabel("Retrieval Top K:"))
        self.topk_spin = QComboBox()
        self.topk_spin.addItems(["3", "5", "10", "15"])
        self.topk_spin.setCurrentIndex(1)
        retrieval_layout.addWidget(self.topk_spin, 1)
        
        # 分块设置
        chunk_layout = QHBoxLayout()
        chunk_layout.addWidget(QLabel("Chunk Size:"))
        self.chunk_size_spin = QComboBox()
        self.chunk_size_spin.addItems(["256", "512", "1024", "2048"])
        self.chunk_size_spin.setCurrentIndex(1)
        chunk_layout.addWidget(self.chunk_size_spin, 1)
        
        # 高级选项
        self.advanced_check = QCheckBox("Enable Advanced Retrieval")
        self.advanced_check.setChecked(True)
        
        self.rerank_check = QCheckBox("Enable Re-ranking")
        self.rerank_check.setChecked(True)
        
        self.hybrid_check = QCheckBox("Hybrid Search (Vector + Keyword)")
        self.hybrid_check.setChecked(False)
        
        layout.addLayout(model_layout)
        layout.addLayout(retrieval_layout)
        layout.addLayout(chunk_layout)
        layout.addWidget(self.advanced_check)
        layout.addWidget(self.rerank_check)
        layout.addWidget(self.hybrid_check)
        layout.addStretch()
        
        return group
    
    def create_query_group(self):
        """创建查询组"""
        group = QGroupBox("Query Input")
        layout = QVBoxLayout(group)
        
        self.query_input = QTextEdit()
        self.query_input.setPlaceholderText("Enter your question here...")
        self.query_input.setMinimumHeight(100)
        layout.addWidget(self.query_input)
        
        # 查询按钮
        btn_layout = QHBoxLayout()
        self.query_btn = QPushButton("Run RAG Query")
        self.query_btn.setObjectName("queryButton")
        self.query_btn.setIcon(QIcon.fromTheme("system-search"))
        self.query_btn.clicked.connect(self.run_query)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_btn.clicked.connect(self.clear_query)
        
        btn_layout.addWidget(self.query_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)
        
        return group
    
    def create_results_tabs(self):
        """创建结果标签页"""
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setDocumentMode(True)
        
        # 回答结果标签页
        answer_tab = QWidget()
        answer_layout = QVBoxLayout(answer_tab)
        answer_layout.setContentsMargins(5, 5, 5, 5)
        
        self.answer_output = QTextEdit()
        self.answer_output.setReadOnly(True)
        self.answer_output.setPlaceholderText("Generated answer will appear here...")
        self.answer_output.setMinimumHeight(200)
        
        answer_layout.addWidget(QLabel("Generated Answer:"))
        answer_layout.addWidget(self.answer_output, 1)
        
        tabs.addTab(answer_tab, "Answer")
        
        # 检索结果标签页
        retrieval_tab = QWidget()
        retrieval_layout = QVBoxLayout(retrieval_tab)
        retrieval_layout.setContentsMargins(5, 5, 5, 5)

        self.retrieval_output = QTextEdit()
        self.retrieval_output.setReadOnly(True)
        self.retrieval_output.setPlaceholderText("retrieval content will appear here...")
        self.retrieval_output.setMinimumHeight(200)
        
        # self.retrieval_table = QTableWidget()
        # self.retrieval_table.setColumnCount(5)
        # self.retrieval_table.setHorizontalHeaderLabels(["ID", "Content"])
        # self.retrieval_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        # self.retrieval_table.setColumnWidth(0, 50)
        # self.retrieval_table.setColumnWidth(1, 280)
        # self.retrieval_table.setColumnWidth(2, 60)
        # self.retrieval_table.setColumnWidth(3, 70)
        # self.retrieval_table.verticalHeader().setVisible(False)
        # self.retrieval_table.setEditTriggers(QTableWidget.NoEditTriggers)
        # self.retrieval_table.setSelectionBehavior(QTableWidget.SelectRows)
        # self.retrieval_table.setSortingEnabled(True)

        retrieval_layout.addWidget(QLabel("Retrieved Contexts:"))
        retrieval_layout.addWidget(self.retrieval_output, 1)
        
        
        tabs.addTab(retrieval_tab, "Retrieved Contexts")
        
        # 处理过程标签页
        process_tab = QWidget()
        process_layout = QVBoxLayout(process_tab)
        
        self.process_output = QTextEdit()
        self.process_output.setReadOnly(True)
        self.process_output.setPlaceholderText("Processing steps will be shown here...")
        
        process_layout.addWidget(QLabel("Processing Steps:"))
        process_layout.addWidget(self.process_output, 1)
        
        tabs.addTab(process_tab, "Processing")
        
        return tabs
    
    def load_files_from_directory(self):
        """加载目录中的文件"""
        documents_path = manager.rag_example.rag_documents_path
        if not os.path.exists(documents_path):
            os.makedirs(documents_path)
            return

        files=[]
        for file_name in os.listdir(documents_path):
            files.append(file_name)

        return files

    def init_mock_data(self):
        """初始化模拟文档数据"""
        mock_docs = self.load_files_from_directory()
        
        for doc in mock_docs:
            item = QListWidgetItem(doc)
            item.setIcon(QIcon.fromTheme("text-plain"))
            self.doc_list.addItem(item)
    
    
    
    def toggle_delete_button(self):
        """切换删除按钮状态"""
        self.delete_btn.setEnabled(len(self.doc_list.selectedItems()) > 0)
    
    def upload_documents(self):
        """上传文档处理"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Documents",
            "",
            "Documents (*.pdf *.docx *.txt *.pptx *.xlsx);;All Files (*)"
        )
        
        if files:
            for file in files:
                file_name = file.split('/')[-1]
                item = QListWidgetItem(file_name)
                item.setIcon(QIcon.fromTheme("text-plain"))
                self.doc_list.addItem(item)

                # 将文件复制到 manager 的 rag_documents_path
                target_path = os.path.join(manager.rag_example.rag_documents_path, file_name)
                shutil.copy(file, target_path)
                manager.rag_example.upload_document(target_path)
            
            self.status_label.setText(f"{len(files)} document(s) added successfully")
    
    def delete_document(self):
        """删除选中的文档"""
        selected_items = self.doc_list.selectedItems()
        if not selected_items:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(selected_items)} selected document(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for item in selected_items:
                file_name=item.text()
                file_path = os.path.join(manager.rag_example.rag_documents_path, file_name)
                os.remove(file_path)
                self.doc_list.takeItem(self.doc_list.row(item))
            self.status_label.setText(f"{len(selected_items)} document(s) deleted")

    def reload_to_vectorstore(self):
        """将文档重新加载到向量存储中"""
        self.status_label.setText("Clear vectorstore...")
        manager.rag_example.delete_vectorstore_all()
        self.status_label.setText("Reload documents to vectorstore...")
        manager.rag_example.upload_document()
        self.status_label.setText("Reload complete")
    
    def clear_query(self):
        """清除查询和结果"""
        self.query_input.clear()
        self.answer_output.clear()
        self.retrieval_output.clear()
        self.process_output.clear()
        self.status_label.setText("Query cleared")
    
    def run_query(self):
        """执行查询（模拟）"""
        query = self.query_input.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a query before running.")
            return
        
        # 更新UI状态
        self.query_btn.setEnabled(False)
        self.query_btn.setText("Processing...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 显示处理步骤
        self.process_output.clear()
        self.process_output.append(f"<b>Starting RAG process for query:</b> {query}")
        self.process_output.append("")
        
        # 模拟处理延迟
        QApplication.processEvents()
        
        # 模拟检索过程
        self.simulate_retrieval_process(query)
        
        # 模拟生成答案
        self.simulate_generated_answer(query)
        
        # 恢复UI状态
        self.query_btn.setEnabled(True)
        self.query_btn.setText("Run RAG Query")
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Query completed: '{query}'")
    
    def simulate_retrieval_process(self, query):
        """模拟检索过程"""
        # 显示检索配置
        config = {
            "model": self.model_combo.currentText(),
            "top_k": self.topk_spin.currentText(),
            "chunk_size": self.chunk_size_spin.currentText(),
            "advanced": self.advanced_check.isChecked(),
            "rerank": self.rerank_check.isChecked(),
            "hybrid": self.hybrid_check.isChecked()
        }
        
        self.process_output.append("<b>Using configuration:</b>")
        self.process_output.append(f" - Model: {config['model']}")
        self.process_output.append(f" - Top K: {config['top_k']}")
        self.process_output.append(f" - Chunk Size: {config['chunk_size']}")
        self.process_output.append(f" - Advanced Retrieval: {'Enabled' if config['advanced'] else 'Disabled'}")
        self.process_output.append(f" - Re-ranking: {'Enabled' if config['rerank'] else 'Disabled'}")
        self.process_output.append(f" - Hybrid Search: {'Enabled' if config['hybrid'] else 'Disabled'}")
        self.process_output.append("")
        
        # 模拟文档处理
        doc_count = self.doc_list.count()
        self.process_output.append(f"<b>Processing {doc_count} documents:</b>")
        self.process_output.append(" - Loading and chunking documents...")
        QApplication.processEvents()
        
        # 模拟检索
        self.process_output.append(" - Embedding query and documents...")
        QApplication.processEvents()
        
        # 模拟重排序
        if config["rerank"]:
            self.process_output.append(" - Applying re-ranking to results...")
            QApplication.processEvents()
        
        
        # 生成模拟数据
        documents = [
            "Research Paper: AI in Healthcare.pdf",
            "Technical Manual v4.2.pdf",
            "Knowledge Base Articles.txt",
            "Annual Report 2023.docx",
            "Product Specifications.xlsx"
        ]
        
        self.process_output.append(f"<b>Retrieved {len(documents)} relevant contexts:</b>")
        
    @pyqtSlot(str)
    def display_in_editor(self, content):
        cursor = self.answer_output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(content)
        self.answer_output.setTextCursor(cursor)
        self.answer_output.ensureCursorVisible()

    @pyqtSlot(str)
    def update_retrieval_table(self, content):
        cursor = self.retrieval_output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(content)
        self.retrieval_output.setTextCursor(cursor)
        self.retrieval_output.ensureCursorVisible()


    @pyqtSlot(str)
    def update_status_label(self, text):
        self.status_label.setText(text)

    def simulate_generated_answer(self, query):
        """生成答案"""

        class StreamWorker(QThread):
            answer_output = pyqtSignal(str)
            retrieval_table = pyqtSignal(str)
            status_label = pyqtSignal(str)
            # done = pyqtSignal()

            def __init__(self, query, topk, streamer):
                super().__init__()
                self.query = query
                self.topk = topk
                self.streamer = streamer

            def run(self):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._run_stream())
                loop.close()

            async def _run_stream(self):
                async for token in self.streamer.chat_stream(self.query, self.topk):
                    # self.update.emit(token)
                    line = token
                    if line.startswith("event: context"):
                        # 下一行就是 context 内容
                        mode = "context"
                    elif line.startswith("event: token"):
                        mode = "token"
                    elif line.startswith("event: done"):
                        # ✅ 接收结束标志
                        # self.update_text.emit("回答完成")
                        break
                    content = line
                    # print(content)
                    if mode == "context":
                        self.retrieval_table.emit(content)
                    elif mode == "token":
                        content = content[len("event: token data: "):]
                        self.answer_output.emit(content)
                self.status_label.emit("Rag query finished.")

        # 显示生成过程
        self.process_output.append("<b>Generating answer using retrieved contexts:</b>")
        self.process_output.append(" - Synthesizing information from relevant passages...")
        QApplication.processEvents()
        
        # 生成答案
        # answer = manager.rag_example.chat(query,k=int(self.topk_spin.currentText()))
        self.worker=StreamWorker(query,int(self.topk_spin.currentText()),manager.rag_example)
        self.worker.answer_output.connect(self.display_in_editor)
        self.worker.retrieval_table.connect(self.update_retrieval_table)
        self.worker.status_label.connect(self.update_status_label)
        self.worker.start()

        
        # self.answer_output.setHtml(f"""
        #     <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #3498db;'>
        #         <p style='font-size: 14px; color: #2c3e50;'>{answer}</p>
        #         <p style='font-size: 12px; color: #7f8c8d; margin-top: 10px;'>
        #             <b>Source:</b> Generated using {self.model_combo.currentText()} model with retrieval from {self.doc_list.count()} documents
        #         </p>
        #     </div>
        # """)
        
        self.process_output.append(" - Answer generation completed")
        self.process_output.append("<b style='color: #27ae60;'>Process completed successfully!</b>")


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建主窗口进行测试
    main_win = QWidget()
    main_win.setWindowTitle("RAG System - Test Page")
    main_win.setGeometry(100, 100, 1200, 800)
    
    layout = QVBoxLayout(main_win)
    
    # 添加标题
    title = QLabel("RAG System Integration Test")
    title.setFont(QFont("Arial", 18, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("color: #2c3e50; padding: 15px;")
    layout.addWidget(title)
    
    # 添加说明
    desc = QLabel("This is a test page demonstrating the RagPage widget integrated into a larger application.")
    desc.setFont(QFont("Arial", 10))
    desc.setAlignment(Qt.AlignCenter)
    desc.setStyleSheet("color: #7f8c8d; padding-bottom: 15px;")
    layout.addWidget(desc)
    
    # 添加分割线
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line)
    
    # 添加RAG页面
    rag_page = RagPage()
    layout.addWidget(rag_page, 1)  # 1表示使用所有可用空间
    
    # 添加底部状态栏
    footer = QLabel("RAG System v1.0 © 2024")
    footer.setFont(QFont("Arial", 9))
    footer.setAlignment(Qt.AlignCenter)
    footer.setStyleSheet("color: #95a5a6; padding: 10px; border-top: 1px solid #ddd;")
    layout.addWidget(footer)
    
    main_win.show()
    sys.exit(app.exec_())