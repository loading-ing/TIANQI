import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTextEdit, QLineEdit, QPushButton, QScrollArea, QLabel)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QTextCursor

from example.manager import Manager

manager=Manager()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 对话助手")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置主窗口部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 创建标题栏
        self.create_title_bar()
        
        # 创建聊天区域
        self.create_chat_area()
        
        # 创建输入区域
        self.create_input_area()
        
        # 设置样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 18px;
                padding: 8px 15px;
                font-size: 14px;
                margin: 10px;
            }
            QPushButton {
                background-color: #10a37f;
                color: white;
                border: none;
                border-radius: 18px;
                padding: 8px 20px;
                font-size: 14px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #0d8a6a;
            }
            QPushButton:pressed {
                background-color: #0b7258;
            }
            #title_bar {
                background-color: #10a37f;
                color: white;
                padding: 10px;
            }
            #chat_area {
                background-color: white;
                border: none;
            }
            .user_message {
                background-color: #f0f0f0;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 50px 5px 20px;
            }
            .ai_message {
                background-color: #e3f2fd;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 20px 5px 50px;
            }
        """)
    
    def create_title_bar(self):
        """创建标题栏"""
        title_bar = QWidget()
        title_bar.setObjectName("title_bar")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel("AI 对话助手")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        self.main_layout.addWidget(title_bar)
    
    def create_chat_area(self):
        """创建聊天显示区域"""
        self.chat_area = QTextEdit()
        self.chat_area.setObjectName("chat_area")
        self.chat_area.setReadOnly(True)
        self.chat_area.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # 使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.chat_area)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.main_layout.addWidget(scroll_area, 1)
    
    def create_input_area(self):
        """创建用户输入区域"""
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(0, 0, 0, 10)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入您的问题...")
        
        self.send_button = QPushButton("发送")
        self.send_button.setFixedSize(QSize(80, 36))
        self.send_button.clicked.connect(self.send_message)
        
        # 按回车键也可以发送消息
        self.input_field.returnPressed.connect(self.send_message)
        
        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(self.send_button)
        
        self.main_layout.addWidget(input_widget)
    
    def send_message(self):
        """发送消息处理"""
        message = self.input_field.text().strip()
        if message:
            # 添加用户消息到聊天区
            self.add_message("user", message)
            
            # 清空输入框
            self.input_field.clear()
            
            # 模拟AI回复
            self.simulate_ai_response(message)
    
    def add_message(self, sender, text):
        """添加消息到聊天区域"""
        if sender == "user":
            css_class = "user_message"
            prefix = "您: "
        else:
            css_class = "ai_message"
            prefix = "AI: "
        
        # 使用HTML格式添加消息
        html = f"""
        <div class="{css_class}">
            <strong>{prefix}</strong>{text}
        </div>
        """
        
        # 将光标移动到最后
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # 插入HTML
        cursor.insertHtml(html)
        
        # 添加换行
        cursor.insertBlock()
        
        # 滚动到底部
        self.chat_area.ensureCursorVisible()
    
    def simulate_ai_response(self, user_message):
        """模拟AI回复"""
        # 在实际应用中，这里应该调用AI模型的API
        # 这里只是简单的模拟回复
        
        # 延迟1秒模拟AI思考时间
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self._send_ai_response(user_message))

    def casual_ai_response(self, user_message):
        # 延迟1秒模拟AI思考时间
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1000, lambda: self._send_ai_response(user_message))
    
    def _send_ai_response(self, user_message):
        response=manager.chat(user_message)

        self.add_message("ai", response)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())