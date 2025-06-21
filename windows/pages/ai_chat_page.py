import sys
import random
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QTextEdit, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QFrame, QGroupBox, QTabWidget,
    QLineEdit, QScrollArea, QSizePolicy, QToolButton, QMenu, QAction, QCheckBox,
    QFileDialog, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QTextCursor, QPalette
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import networkx as nx
import numpy as np
import asyncio
from example.manager import manager

class AIChatPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.init_data()
        
    def setup_ui(self):
        """设置UI界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("Causal AI Dialogue System")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; padding-bottom: 10px; border-bottom: 2px solid #3498db;")
        main_layout.addWidget(title_label)
        
        # 创建中心区域
        splitter = QSplitter(Qt.Horizontal)

        # 状态栏
        self.status_label = QLabel("Ready to start causal dialogue")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        
        # 左侧面板：对话历史和设置
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # 对话历史部分
        history_group = self.create_history_group()
        left_layout.addWidget(history_group)
        
        # 模型设置部分
        settings_group = self.create_settings_group()
        left_layout.addWidget(settings_group)
        
        # 右侧面板：对话交互和可视化
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # 对话显示区域
        chat_display_group = self.create_chat_display_group()
        right_layout.addWidget(chat_display_group, 3)  # 3/4空间
        
        # 对话输入区域
        chat_input_group = self.create_chat_input_group()
        right_layout.addWidget(chat_input_group, 1)  # 1/4空间
        
        # 添加到分割器
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter, 1)  # 使用所有可用空间
        
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
            AIChatPage {
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
            QListWidget, QTextEdit, QLineEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
            }
            QScrollArea {
                border: none;
                background: transparent;
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
            #sendButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: 1px solid #2980b9;
            }
            #sendButton:hover {
                background-color: #2980b9;
            }
            #newChatButton, #exportButton {
                background-color: #2ecc71;
                color: white;
                border: 1px solid #27ae60;
            }
            #newChatButton:hover, #exportButton:hover {
                background-color: #27ae60;
            }
            #clearButton, #deleteButton {
                background-color: #e74c3c;
                border: 1px solid #c0392b;
                color: white;
            }
            #clearButton:hover, #deleteButton:hover {
                background-color: #c0392b;
            }
            .message-user {
                background-color: #d6eaf8;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
            }
            .message-ai {
                background-color: #e8f8f5;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
            }
            .message-system {
                background-color: #fef9e7;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 0;
            }
            .causal-node {
                font-weight: bold;
                color: #2c3e50;
            }
        """)
    
    def create_history_group(self):
        """创建对话历史组"""
        group = QGroupBox("Dialogue History")
        layout = QVBoxLayout(group)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.new_chat_btn = QPushButton("New Chat")
        self.new_chat_btn.setObjectName("newChatButton")
        self.new_chat_btn.setIcon(QIcon.fromTheme("document-new"))
        self.new_chat_btn.clicked.connect(self.new_chat)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setObjectName("deleteButton")
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.clicked.connect(self.delete_chat)
        self.delete_btn.setEnabled(False)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.setObjectName("exportButton")
        self.export_btn.setIcon(QIcon.fromTheme("document-save"))
        self.export_btn.clicked.connect(self.export_chat)
        self.export_btn.setEnabled(False)
        
        btn_layout.addWidget(self.new_chat_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
        # 对话历史列表
        self.history_list = QListWidget()
        self.history_list.setSelectionMode(QListWidget.SingleSelection)
        self.history_list.itemSelectionChanged.connect(self.toggle_history_buttons)
        layout.addWidget(self.history_list)
        
        return group
    
    def create_settings_group(self):
        """创建设置组"""
        group = QGroupBox("AI Configuration")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        
        try:
            self.model_config=manager.get_model_config()
            # print(self.model_config)
        except:
            self.model_config=None
            self.status_label.setText("server not connected")

        if self.model_config:
            model_names=[key for key in self.model_config["session"]]
        else:
            model_names=["no model"]

        # 模型选择
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Causal Model:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(
            model_names)
        self.model_combo.setCurrentIndex(0)
        model_layout.addWidget(self.model_combo, 1)
        
        # 推理长度
        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Max Length:"))
        self.depth_slider = QComboBox()
        self.depth_slider.addItems(["512", "1024", "2048", "4096"])
        self.depth_slider.setCurrentIndex(3)
        depth_layout.addWidget(self.depth_slider, 1)
        
        # temperature
        explain_layout = QHBoxLayout()
        explain_layout.addWidget(QLabel("temperature:"))
        self.explain_combo = QComboBox()
        self.explain_combo.addItems(["0.7", "0.8", "0.9", "1.0"])
        self.explain_combo.setCurrentIndex(0)
        explain_layout.addWidget(self.explain_combo, 1)
        
        # 高级选项
        self.counterfactual_check = QCheckBox("Enable Counterfactual Reasoning")
        self.counterfactual_check.setChecked(True)
        
        self.visualization_check = QCheckBox("Generate Causal Graphs")
        self.visualization_check.setChecked(True)
        
        self.data_check = QCheckBox("Include Data Analysis")
        self.data_check.setChecked(False)
        
        layout.addLayout(model_layout)
        layout.addLayout(depth_layout)
        layout.addLayout(explain_layout)
        layout.addWidget(self.counterfactual_check)
        layout.addWidget(self.visualization_check)
        layout.addWidget(self.data_check)
        layout.addStretch()
        
        return group
    
    def create_chat_display_group(self):
        """创建对话显示组"""
        group = QGroupBox("Dialogue")
        layout = QVBoxLayout(group)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setDocumentMode(True)
        
        # 对话标签页
        chat_tab = QWidget()
        chat_layout = QVBoxLayout(chat_tab)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # 对话显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: white;")
        self.chat_display.setHtml("<div align='center' style='color:#95a5a6; padding:50px;'>Start a new conversation to begin</div>")
        
        # 包装在滚动区域中
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.chat_display)
        
        chat_layout.addWidget(scroll_area)
        self.tab_widget.addTab(chat_tab, "Dialogue")
        
        # 因果图标签页
        graph_tab = QWidget()
        graph_layout = QVBoxLayout(graph_tab)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        
        # 因果图显示区域
        self.figure = plt.figure(figsize=(8, 6), facecolor='#f5f7fa')
        self.canvas = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas)
        
        self.tab_widget.addTab(graph_tab, "Causal Graph")
        
        # 分析标签页
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        analysis_layout.setContentsMargins(5, 5, 5, 5)
        
        self.analysis_output = QTextEdit()
        self.analysis_output.setReadOnly(True)
        self.analysis_output.setPlaceholderText("Detailed causal analysis will appear here...")
        analysis_layout.addWidget(self.analysis_output)
        
        self.tab_widget.addTab(analysis_tab, "Analysis")
        
        layout.addWidget(self.tab_widget)
        
        return group
    
    def create_chat_input_group(self):
        """创建对话输入组"""
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your question about causality here...")
        self.chat_input.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendButton")
        self.send_btn.setIcon(QIcon.fromTheme("mail-send"))
        self.send_btn.clicked.connect(self.send_message)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("clearButton")
        self.clear_btn.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_btn.clicked.connect(self.clear_input)
        
        input_layout.addWidget(self.chat_input, 5)
        input_layout.addWidget(self.send_btn, 1)
        input_layout.addWidget(self.clear_btn, 1)
        
        # 快捷问题按钮
        quick_questions = QWidget()
        quick_layout = QHBoxLayout(quick_questions)
        quick_layout.setContentsMargins(0, 5, 0, 0)
        
        self.quick_btn = QToolButton()
        self.quick_btn.setText("Quick Questions ▼")
        self.quick_btn.setPopupMode(QToolButton.InstantPopup)
        
        quick_menu = QMenu()
        questions = [
            "What is the causal effect of X on Y?",
            "How to identify confounding variables?",
            "Explain Simpson's paradox with an example",
            "What is the difference between correlation and causation?",
            "How to design a causal experiment?",
            "Explain instrumental variables"
        ]
        
        for q in questions:
            action = QAction(q, self)
            action.triggered.connect(lambda checked, text=q: self.set_question(text))
            quick_menu.addAction(action)
        
        self.quick_btn.setMenu(quick_menu)
        
        quick_layout.addWidget(QLabel("Examples:"))
        quick_layout.addWidget(self.quick_btn)
        quick_layout.addStretch()
        
        layout.addLayout(input_layout)
        layout.addWidget(quick_questions)
        
        return group
    
    def init_data(self):
        """初始化数据"""
        # 初始化对话历史
        self.conversations = {
            "Conversation 1": [],
            "Conversation 2": [],
            "Sample: Education Analysis": [
                ("system", "New conversation started with CausalGPT-4"),
                ("user", "What is the causal effect of smaller class sizes on student performance?"),
                ("ai", "Research generally shows that smaller class sizes have a positive causal effect on student performance, especially in early education. The Tennessee STAR experiment provides strong evidence for this relationship."),
                ("user", "What are the potential confounding variables?"),
                ("ai", "Key confounders include teacher quality, school resources, socioeconomic status of students, and parental involvement. These factors may correlate with both class size and student performance.")
            ]
        }
        
        # 添加到历史列表
        for title in self.conversations:
            item = QListWidgetItem(title)
            if "Sample" in title:
                item.setIcon(QIcon.fromTheme("help-about"))
            else:
                item.setIcon(QIcon.fromTheme("text-plain"))
            self.history_list.addItem(item)
        
        # 选择最后一个对话
        self.history_list.setCurrentRow(self.history_list.count() - 1)
        self.current_conversation = self.history_list.currentItem().text()
        self.update_chat_display()
    
    def toggle_history_buttons(self):
        """切换历史按钮状态"""
        selected = self.history_list.selectedItems()
        self.delete_btn.setEnabled(bool(selected))
        self.export_btn.setEnabled(bool(selected))
        
        if selected:
            self.current_conversation = selected[0].text()
            self.update_chat_display()
    
    def new_chat(self):
        """创建新对话"""
        conversation_name = f"Conversation {self.history_list.count() + 1}"
        self.conversations[conversation_name] = [
            ("system", f"New conversation started with {self.model_combo.currentText()}")
        ]
        
        item = QListWidgetItem(conversation_name)
        item.setIcon(QIcon.fromTheme("text-plain"))
        self.history_list.addItem(item)
        self.history_list.setCurrentItem(item)
        
        self.status_label.setText(f"New conversation started: {conversation_name}")
    
    def delete_chat(self):
        """删除当前对话"""
        selected = self.history_list.selectedItems()
        if not selected:
            return
        
        conversation = selected[0].text()
        if "Sample" in conversation:
            QMessageBox.warning(self, "Cannot Delete", "Sample conversations cannot be deleted.")
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete '{conversation}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.history_list.row(selected[0])
            self.history_list.takeItem(row)
            del self.conversations[conversation]
            
            if self.history_list.count() > 0:
                self.history_list.setCurrentRow(0)
            else:
                self.current_conversation = ""
                self.chat_display.setHtml("<div align='center' style='color:#95a5a6; padding:50px;'>No active conversation</div>")
            
            self.status_label.setText(f"Deleted conversation: {conversation}")
    
    def export_chat(self):
        """导出对话"""
        selected = self.history_list.selectedItems()
        if not selected:
            return
        
        conversation = selected[0].text()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Conversation",
            f"{conversation}.txt",
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Conversation: {conversation}\n")
                    f.write(f"Model: {self.model_combo.currentText()}\n\n")
                    
                    for sender, message in self.conversations[conversation]:
                        prefix = "User: " if sender == "user" else "AI: " if sender == "ai" else "System: "
                        f.write(f"{prefix}{message}\n\n")
                
                self.status_label.setText(f"Exported conversation to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export conversation: {str(e)}")
    
    def clear_input(self):
        """清空输入"""
        self.chat_input.clear()
        self.status_label.setText("Input cleared")
    
    def set_question(self, text):
        """设置问题文本"""
        self.chat_input.setText(text)
        self.chat_input.setFocus()
        self.status_label.setText("Question set from examples")
    
    def update_chat_display(self):
        """更新对话显示"""
        if not self.current_conversation:
            return
        
        conversation = self.conversations[self.current_conversation]
        html = "<div style='font-family: Arial; font-size: 14px;'>"
        
        for sender, message in conversation:
            if sender == "system":
                html += f"<div class='message-system'><b>System:</b> {message}</div>"
            elif sender == "user":
                html += f"<div class='message-user'><b>You:</b> {message}</div>"
            elif sender == "ai":
                # 高亮因果术语
                highlighted = message
                for term in ["causal", "effect", "confounding", "mediation", "instrumental", "counterfactual"]:
                    highlighted = highlighted.replace(term, f"<span class='causal-node'>{term}</span>")
                
                html += f"<div class='message-ai'><b>AI:</b> {highlighted}</div>"
        
        html += "</div>"
        self.chat_display.setHtml(html)
        
        # 滚动到底部
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def send_message(self):
        """发送消息"""
        message = self.chat_input.text().strip()
        if not message:
            return
        

        # 添加到当前对话
        self.conversations[self.current_conversation].append(("user", message))
        self.update_chat_display()
        self.chat_input.clear()
        
        # 更新UI状态
        self.chat_input.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText("AI is generating response...")
        
        self.generate_ai_response(message)
        # 模拟AI处理延迟
        # QTimer.singleShot(1500, lambda: self.generate_ai_response(message))
    
    @pyqtSlot(str)
    def display_in_conversation(self, content):
        conversation=self.conversations[self.current_conversation]
        # print(content)
        # 找到最后一条 AI 消息并拼接 token
        for i in reversed(range(len(conversation))):
            if conversation[i][0] == "ai":
                conversation[i] = ("ai", conversation[i][1] + content)
                # print(conversation[i])
                break

        self.update_chat_display()

    @pyqtSlot(str)
    def update_status_label(self, text):
        self.status_label.setText(text)

    def generate_ai_response(self, user_message):
        """生成AI响应"""

        class StreamWorker(QThread):
            answer_output = pyqtSignal(str)
            status_label = pyqtSignal(str)
            # done = pyqtSignal()

            def __init__(self, query, role, streamer):
                super().__init__()
                self.query = query
                self.role = role
                self.streamer = streamer

            def run(self):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._run_stream())
                loop.close()

            async def _run_stream(self):
                async for token in self.streamer.chat_stream(self.query, self.role):
                    # self.update.emit(token)
                    self.answer_output.emit(token)
                self.status_label.emit("answer finished.")

        try:
            # 获取当前对话
            conversation = self.conversations[self.current_conversation]
            conversation.append(("ai", ""))  # 初始化空回答
            self.update_chat_display()
            
            # 基于用户消息生成响应
            # ai_response = self.generate_causal_response(user_message)
            self.worker=StreamWorker(user_message,"user",manager.casual_example)
            self.worker.answer_output.connect(self.display_in_conversation)
            self.worker.status_label.connect(self.update_status_label)
            self.worker.start()
            
            # # 添加到对话
            # conversation.append(("ai", ai_response))
            
            # # 更新显示
            # self.update_chat_display()
            
            # 生成因果图
            if self.visualization_check.isChecked():
                self.generate_causal_graph(user_message)
            
            # 生成详细分析
            if self.explain_combo.currentIndex() > 0:
                self.generate_analysis(user_message)
            
            # 恢复UI状态
            self.status_label.setText("Response generated")
        
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate response: {str(e)}")
        
        finally:
            self.chat_input.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def generate_causal_response(self, user_message):
        """生成因果响应（模拟）"""
        # 根据用户消息生成不同的响应
        model = self.model_combo.currentText()
        depth = self.depth_slider.currentText()
        explain_level = self.explain_combo.currentText()
        counterfactual = self.counterfactual_check.isChecked()

        class StreamWorker(QThread):
            answer_output = pyqtSignal(str)
            retrieval_table = pyqtSignal(str)
            status_label = pyqtSignal(str)
            # done = pyqtSignal()

            def __init__(self, query, role, streamer):
                super().__init__()
                self.query = query
                self.role = role
                self.streamer = streamer

            def run(self):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self._run_stream())
                loop.close()

            async def _run_stream(self):
                async for token in self.streamer.chat_stream(self.query, self.role):
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

        # 调用AI对话模型
        response = manager.casual_chat(user_message)

        return response
        
        # # 查找匹配的响应
        # for q, a in responses.items():
        #     if q.lower() in user_message.lower():
        #         return a
        
        # # 默认响应
        # return (f"Based on {model} analysis with {depth} reasoning depth:\n\n"
        #         f"Causal analysis of '{user_message}' suggests several important considerations. "
        #         "First, we must identify potential confounders that might affect the relationship. "
        #         "Second, the causal mechanism likely involves mediation pathways. "
        #         f"{'Counterfactual analysis indicates ' if counterfactual else ''}"
        #         "Further investigation with specific data would provide more precise estimates.")
    
    def generate_causal_graph(self, user_message):
        """生成因果图（模拟）"""
        # 清除之前的图形
        self.figure.clear()
        
        # 创建有向图
        G = nx.DiGraph()
        
        # 根据用户消息添加节点
        keywords = ["education", "health", "economy", "drug", "policy", "behavior", "environment", "technology"]
        selected_keywords = random.sample(keywords, min(4, len(keywords)))
        
        # 添加节点
        for word in selected_keywords:
            G.add_node(word.capitalize())
        
        # 添加边
        for i in range(len(selected_keywords)):
            for j in range(i+1, len(selected_keywords)):
                if random.random() > 0.6:  # 随机添加边
                    G.add_edge(
                        selected_keywords[i].capitalize(), 
                        selected_keywords[j].capitalize()
                    )
        
        # 绘制图形
        ax = self.figure.add_subplot(111)
        pos = nx.spring_layout(G, seed=42)
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='#3498db', alpha=0.8, ax=ax)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, width=2, edge_color='#7f8c8d', alpha=0.6, ax=ax)
        
        # 绘制标签
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', font_color='white', ax=ax)
        
        # 设置标题
        ax.set_title(f"Causal Relationships for: '{user_message[:20]}...'", fontsize=14)
        
        # 移除坐标轴
        ax.axis('off')
        
        # 刷新画布
        self.canvas.draw()
        
        # 切换到因果图标签页
        # self.tab_widget.setCurrentIndex(1)
    
    def generate_analysis(self, user_message):
        """生成详细分析（模拟）"""
        explain_level = self.explain_combo.currentText()
        model = self.model_combo.currentText()
        
        # 根据解释级别生成不同详细程度的分析
        if explain_level == "Minimal":
            analysis = f"Brief analysis using {model}: The causal relationship involves several factors. Further investigation recommended."
        elif explain_level == "Moderate":
            analysis = (
                f"Moderate analysis using {model}:\n\n"
                "1. Identified 3 potential confounders\n"
                "2. Estimated causal effect: 0.45 (95% CI: 0.32-0.58)\n"
                "3. Mediation analysis shows 30% indirect effect\n"
                "Recommendation: Collect more data on identified confounders."
            )
        elif explain_level == "Detailed":
            analysis = (
                f"Detailed analysis using {model}:\n\n"
                "Causal Query: " + user_message + "\n\n"
                "Method: Propensity Score Matching with Nearest Neighbor\n\n"
                "Results:\n"
                " - Average Treatment Effect (ATE): 0.42\n"
                " - Standard Error: 0.08\n"
                " - 95% Confidence Interval: [0.27, 0.57]\n\n"
                "Sensitivity Analysis:\n"
                " - The result is robust to unmeasured confounding at Gamma=1.8\n"
                " - Rosenbaum bounds indicate moderate sensitivity\n\n"
                "Key Assumptions:\n"
                "1. Conditional exchangeability\n"
                "2. Positivity\n"
                "3. Consistency\n\n"
                "Recommendations:\n"
                "- Collect data on possible unmeasured confounders\n"
                "- Consider instrumental variable approach\n"
                "- Replicate analysis with different matching methods"
            )
        else:  # Technical
            analysis = (
                f"Technical analysis using {model}:\n\n"
                "Causal Model Specification:\n"
                "Y = β₀ + β₁X + β₂Z + β₃XZ + ε\n\n"
                "Identification Strategy:\n"
                "- Backdoor criterion satisfied by conditioning on {Z1, Z2, Z3}\n"
                "- Frontdoor path identified: X → M → Y\n\n"
                "Estimation:\n"
                "- Two-stage least squares (2SLS) with IV: Rainfall\n"
                "- First stage F-statistic: 28.7 (p < 0.001)\n"
                "- Sargan test for overidentification: χ²=3.2 (p=0.20)\n\n"
                "Results:\n"
                "| Coefficient | Estimate | Std. Error | t-value | p-value |\n"
                "|-------------|----------|------------|---------|---------|\n"
                "| X (Treatment) | 0.538   | 0.087      | 6.18    | <0.001  |\n"
                "| Z1          | -0.212  | 0.045      | -4.71   | <0.001  |\n"
                "| Z2          | 0.187   | 0.032      | 5.84    | <0.001  |\n"
                "| X*Z1        | 0.098   | 0.021      | 4.67    | <0.001  |\n\n"
                "Diagnostics:\n"
                "- R² = 0.68\n"
                "- Breusch-Pagan test for heteroscedasticity: χ²=15.3 (p=0.08)\n"
                "- Durbin-Watson: 1.92\n\n"
                "Conclusion: Statistically significant causal effect of X on Y (β=0.538, p<0.001)"
            )
        
        self.analysis_output.setPlainText(analysis)
        
        # 切换到分析标签页
        # self.tab_widget.setCurrentIndex(2)


# 测试代码
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 创建主窗口进行测试
    main_win = QWidget()
    main_win.setWindowTitle("Causal AI Dialogue System")
    main_win.setGeometry(100, 100, 1200, 800)
    
    layout = QVBoxLayout(main_win)
    
    # 添加标题
    title = QLabel("Causal Inference AI Assistant")
    title.setFont(QFont("Arial", 18, QFont.Bold))
    title.setAlignment(Qt.AlignCenter)
    title.setStyleSheet("color: #2c3e50; padding: 15px;")
    layout.addWidget(title)
    
    # 添加说明
    desc = QLabel("Explore causal relationships through interactive dialogue with AI")
    desc.setFont(QFont("Arial", 10))
    desc.setAlignment(Qt.AlignCenter)
    desc.setStyleSheet("color: #7f8c8d; padding-bottom: 15px;")
    layout.addWidget(desc)
    
    # 添加分割线
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    layout.addWidget(line)
    
    # 添加聊天页面
    chat_page = AIChatPage()
    layout.addWidget(chat_page, 1)  # 1表示使用所有可用空间
    
    # 添加底部状态栏
    footer = QLabel("Causal AI Dialogue System v1.0 © 2024 | Powered by PyQt5")
    footer.setFont(QFont("Arial", 9))
    footer.setAlignment(Qt.AlignCenter)
    footer.setStyleSheet("color: #95a5a6; padding: 10px; border-top: 1px solid #ddd;")
    layout.addWidget(footer)
    
    main_win.show()
    sys.exit(app.exec_())