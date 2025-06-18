from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import asyncio

from example.manager import manager

class AIChatPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 聊天记录区（滚动）
        self.chat_area = QVBoxLayout()
        self.chat_area.setAlignment(Qt.AlignTop)

        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.chat_area)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_content)

        layout.addWidget(self.scroll_area)

        # 加一个底部占位器！！
        self.bottom_spacer = QLabel()
        self.chat_area.addWidget(self.bottom_spacer)

        # 输入框区
        input_layout = QHBoxLayout()

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("请输入消息...")
        self.input_box.setFixedHeight(50)
        self.input_box.setFont(QFont("Arial", 12))
        self.input_box.installEventFilter(self)

        send_button = QPushButton("发送")
        send_button.setFixedWidth(80)
        send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_box)
        input_layout.addWidget(send_button)

        layout.addLayout(input_layout)

    def add_message(self, sender, message, align_right=False):
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

        frame = QFrame()
        frame.setLayout(container)

        # 在底部spacer前面插入
        self.chat_area.insertWidget(self.chat_area.count() - 1, frame)

        # 重要！！滚动到底部
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )


    def send_message(self):
        user_text = self.input_box.toPlainText().strip()
        if user_text == "":
            return

        # 显示用户消息
        self.add_message("你", user_text, align_right=True)

        # 模拟AI回复
        ai_response = asyncio.run(self.get_ai_response(user_text))
        self.add_message("AI", ai_response, align_right=False)

        # 清空输入框
        self.input_box.clear()


    def get_ai_response(self, prompt):
        # TODO: 这里可以替换为真正的API推理
        response = manager.casual_chat(prompt)
        return response

