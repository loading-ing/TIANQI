import sys
import time
import live2d.v3 as live2d
import threading
import random
import textwrap
import os
from PyQt5.QtWidgets import (
    QApplication, QOpenGLWidget, QLabel, QLineEdit, 
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton,
    QGraphicsOpacityEffect
)
from PyQt5.QtWidgets import QWidget, QLabel, QScrollArea, QVBoxLayout, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QEvent, QEasingCurve

from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QThread, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QFontMetrics, QCursor
import asyncio

from windows.main import MainWindow

from example.manager import manager

class ChatBubble(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumWidth(150)
        self.setMaximumWidth(250)
        self.setMinimumHeight(40)
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        
        # 设置气泡样式
        self.setStyleSheet("""
            background-color: #e6f7ff;
            border: 1px solid #91d5ff;
            border-radius: 15px;
            padding: 10px;
            font-size: 14px;
            color: #333;
        """)
        
        # 添加动画效果
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.hide_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.hide_animation.setDuration(1000)
        self.hide_animation.setStartValue(1.0)
        self.hide_animation.setEndValue(0.0)
        self.hide_animation.setEasingCurve(QEasingCurve.InCubic)
        self.hide_animation.finished.connect(self.hide)

    def showEvent(self, event):
        self.animation.start()
        super().showEvent(event)
    
    def hide_bubble(self):
        self.hide_animation.start()
    
    def clear_text(self):
        self.setText("")
    
    def set_text(self, text):
        self.setText(text)
        self.adjustSize()
    
    def append_text(self, text):
        self.setText(self.text()  + text)
        self.adjustSize()

# class ChatBubble(QWidget):
#     def __init__(self, text="", parent=None):
#         super().__init__(parent)

#         self.setMinimumWidth(150)
#         self.setMaximumWidth(250)
#         self.setMinimumHeight(40)

#         # 设置布局
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)

#         # 内容标签
#         self.label = QLabel(text, self)
#         self.label.setWordWrap(True)
#         self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
#         self.label.setStyleSheet("padding: 5px; font-size: 14px; color: #333;")

#         # 滚动区域
#         self.scroll = QScrollArea(self)
#         self.scroll.setWidgetResizable(True)
#         self.scroll.setWidget(self.label)
#         self.scroll.setFrameShape(QScrollArea.NoFrame)
#         self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
#         self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

#         layout.addWidget(self.scroll)

#         # 设置整体样式
#         self.setStyleSheet("""
#             ChatBubble {
#                 background-color: #e6f7ff;
#                 border: 1px solid #91d5ff;
#                 border-radius: 15px;
#             }
#         """)

#         # 动画
#         self.opacity_effect = QGraphicsOpacityEffect(self)
#         self.opacity_effect.setOpacity(0.0)
#         self.setGraphicsEffect(self.opacity_effect)

#         self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
#         self.animation.setDuration(1000)
#         self.animation.setStartValue(0.0)
#         self.animation.setEndValue(1.0)
#         self.animation.setEasingCurve(QEasingCurve.OutCubic)

#         self.hide_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
#         self.hide_animation.setDuration(1000)
#         self.hide_animation.setStartValue(1.0)
#         self.hide_animation.setEndValue(0.0)
#         self.hide_animation.setEasingCurve(QEasingCurve.InCubic)
#         self.hide_animation.finished.connect(self.hide)

#         # 支持双击隐藏
#         self.installEventFilter(self)

#     def set_text(self, text):
#         self.label.setText(text)
#         self.label.adjustSize()

#     def append_text(self, text):
#         self.label.setText(self.label.text() + text)
#         self.label.adjustSize()

#     def showEvent(self, event):
#         self.animation.start()
#         return super().showEvent(event)

#     def hide_bubble(self):
#         self.hide_animation.start()

#     def eventFilter(self, obj, event):
#         if event.type() == QEvent.MouseButtonDblClick:
#             self.hide_bubble()
#             return True
#         return super().eventFilter(obj, event)

class Pet(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        # 设置无边框、置顶和透明背景
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.management_window = None
        
        self.setWindowTitle("天启小助手")
        self.setFixedSize(400, 500)  # 增加高度以容纳输入框
        
        self.pet_model = None
        self.is_dragging = False
        self.drag_position = None
        
        # 创建气泡
        self.bubble = ChatBubble("你好，我是天启小助手！", self)
        self.bubble.hide()
        
        # 创建输入框和按钮
        self.create_input_area()
        
        # 表情计时器
        self.expression_timer = QTimer(self)
        self.expression_timer.timeout.connect(self.random_expression)
        self.expression_timer.start(10000)  # 每10秒随机表情
        
        # 初始化位置
        self.move_to_bottom_right()
    
    def create_input_area(self):
        # 输入区域框架
        self.input_frame = QFrame(self)
        self.input_frame.setGeometry(50, 400, 300, 80)
        self.input_frame.setStyleSheet("""
            background-color: rgba(255, 255, 255, 200);
            border-radius: 15px;
            padding: 10px;
        """)
        self.input_frame.hide()
        
        # 布局
        layout = QVBoxLayout(self.input_frame)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 输入框
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入你想说的话...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 1px solid #91d5ff;
                border-radius: 10px;
                padding: 1px;
                font-size: 14px;
            }
        """)
        self.input_field.returnPressed.connect(self.process_input)
        
        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
            QPushButton:pressed {
                background-color: #096dd9;
            }
        """)
        self.send_button.clicked.connect(self.process_input)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.send_button)
        
        # 添加到主布局
        layout.addWidget(self.input_field)
        layout.addLayout(button_layout)
    
    def move_to_bottom_right(self):
        screen_geo = QApplication.desktop().availableGeometry()
        x = screen_geo.width() - self.width()
        y = screen_geo.height() - self.height()
        self.move(x, y)
    
    def initializeGL(self):
        live2d.glewInit()
        self.pet_model = live2d.LAppModel()
        model_path = "resources/live2d/v3/nn/nn.model3.json"
        
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            # 使用默认模型路径或处理错误
            model_path = os.path.join(os.path.dirname(__file__), "resources/live2d/v3/nn/nn.model3.json")
            if not os.path.exists(model_path):
                print(f"模型文件未找到: {model_path}")
                return
        
        self.pet_model.LoadModelJson(model_path)
        self.startTimer(30)  # 30ms刷新
    
    def resizeGL(self, w, h):
        if self.pet_model:
            self.pet_model.Resize(w, h)
    
    def paintGL(self):
        live2d.clearBuffer()
        if self.pet_model:
            self.pet_model.Update()
            self.pet_model.Draw()
        
        # 更新气泡位置
        self.update_bubble_position()
    
    def update_bubble_position(self):
        # 气泡位于人物头顶
        if self.bubble.isVisible():
            self.bubble.move(250, 50)
            self.bubble.raise_()
    
    def timerEvent(self, event):
        if self.is_dragging:
            x, y = QCursor.pos().x() - self.drag_position.x(), QCursor.pos().y() - self.drag_position.y()
            self.move(x, y)
        
        if self.pet_model:
            # 模拟呼吸效果 - 使用正确的方法名
            time_val = time.time() * 2
            breath = (abs((time_val % 3) - 1.5) - 0.75) * 0.02
            self.set_parameter("ParamBreath", breath)
            
            # 模拟眨眼
            if random.random() < 0.01:
                self.set_parameter("ParamEyeLOpen", 0.0)
                self.set_parameter("ParamEyeROpen", 0.0)
            else:
                self.set_parameter("ParamEyeLOpen", 1.0)
                self.set_parameter("ParamEyeROpen", 1.0)
        
        
        self.update()
    
    def set_parameter(self, param_id, value):
        """设置模型参数的正确方法"""
        # 使用正确的API设置参数
        try:
            # 方法1: 使用SetParamFloat (如果存在)
            if hasattr(self.pet_model, 'SetParamFloat'):
                self.pet_model.SetParamFloat(param_id, value)
            # 方法2: 使用模型内部的模型对象
            elif hasattr(self.pet_model, 'model') and hasattr(self.pet_model.model, 'set_param_float'):
                self.pet_model.model.set_param_float(param_id, value)
            # 方法3: 使用通用方法
            elif hasattr(self.pet_model, 'set_param_float'):
                self.pet_model.set_param_float(param_id, value)
            else:
                # 如果以上方法都不可用，尝试直接设置
                try:
                    self.pet_model.__getattr__('set_param_float')(param_id, value)
                except:
                    pass
        except Exception as e:
            print(f"设置参数错误: {param_id}={value}, {e}")
    
    def random_expression(self):
        if not self.pet_model:
            return
        
        # 随机选择表情
        expressions = ["f01", "f02", "f03", "f04", "f05", "f06", "f07", "f08"]
        expression = random.choice(expressions)
        try:
            self.pet_model.StartMotion("Expressions", expression, 3)
        except:
            try:
                # 尝试不同的方法名
                self.pet_model.start_motion("Expressions", expression, 3)
            except:
                pass
        
        # 随机说话
        if not self.bubble.isVisible():  # 确保气泡未被使用
            if random.random() < 0.3:
                phrases = [
                    "今天天气不错呢",
                    "有什么我可以帮忙的吗？",
                    "工作辛苦了，休息一下吧",
                    "记得多喝水哦",
                    "新的一天要加油呀"
                ]
                self.show_bubble(random.choice(phrases))
    
    def show_bubble(self, text):
        self.bubble.set_text(text)
        self.bubble.show()
        self.update_bubble_position()
        
        # 5秒后自动隐藏气泡
        QTimer.singleShot(5000, self.bubble.hide_bubble)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

        if event.button() == Qt.RightButton:
            print("右键点击：打开管理界面")
            self.open_management_ui()
    
    def open_management_ui(self):
        """
        右键点击，弹出管理界面（MainWindow）
        """
        if self.management_window is None:
            self.management_window = MainWindow()
        self.management_window.show()
        self.management_window.raise_()  # 确保窗口在最前面
        self.management_window.activateWindow()  # 激活窗口
    
    def mouseDoubleClickEvent(self, event):
        """双击事件处理"""
        if event.button() == Qt.LeftButton:
            self.toggle_input_area()
    
    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            event.accept()
    
    def toggle_input_area(self):
        if self.input_frame.isVisible():
            self.input_frame.hide()
            self.input_field.clear()
        else:
            self.input_frame.show()
            self.input_field.setFocus()
    
    @pyqtSlot(str)
    def display_in_bubble(self, content):
        if not self.bubble.isVisible():
            self.bubble.clear_text()
            self.bubble.show()
        self.bubble.append_text(content)
        self.update_bubble_position()

    @pyqtSlot()
    def bubble_done(self):
        # 5秒后自动隐藏气泡
        QTimer.singleShot(10000, self.bubble.hide_bubble)


    def process_input(self):
        class StreamWorker(QThread):
            answer_output = pyqtSignal(str)
            # retrieval_table = pyqtSignal(str)
            # status_label = pyqtSignal(str)
            done = pyqtSignal()

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
                        self.done.emit()
                        break
                    content = line
                    # print(content)
                    if mode == "context":
                        pass
                    elif mode == "token":
                        content = content[len("event: token data: "):]
                        self.answer_output.emit(content)

        text = self.input_field.text().strip()
        if not text:
            return
        
        text = text+"。要求回答句子长度不超过30个字。"

        self.worker=StreamWorker(text,5,manager.rag_example)
        self.worker.answer_output.connect(self.display_in_bubble)
        self.worker.done.connect(self.bubble_done)

        # self.worker.retrieval_table.connect(self.update_retrieval_table)
        # self.worker.status_label.connect(self.update_status_label)
        self.worker.start()
        
        
        # 显示用户消息
        # self.show_bubble(f"你说: {text}")
        
        # 处理输入并生成回复
        # reply = self.generate_reply(text)
        
        # 显示回复
        # QTimer.singleShot(1500, lambda: self.show_bubble(reply))
        
        # 清空输入框并隐藏
        self.input_field.clear()
        QTimer.singleShot(2000, self.input_frame.hide)
    
    def generate_reply(self, text):
        # 简单的回复逻辑
        text = text.lower()
        
        greetings = ["你好", "hi", "hello", "嗨"]
        questions = ["吗？", "么？", "什么", "如何", "怎样", "为什么"]
        thanks = ["谢谢", "thx", "感谢"]
        bye = ["再见", "拜拜", "bye"]
        
        if any(word in text for word in greetings):
            return random.choice(["你好呀！", "很高兴见到你！", "嗨，有什么可以帮你的吗？"])
        
        elif any(word in text for word in questions):
            return random.choice([
                "这个问题很有趣！",
                "让我想想怎么回答...",
                "每个人对这个问题的看法可能不同",
                "我还在学习中，暂时回答不了这个问题"
            ])
        
        elif any(word in text for word in thanks):
            return random.choice(["不客气！", "很高兴能帮到你！", "这是我的荣幸！"])
        
        elif any(word in text for word in bye):
            return random.choice(["再见！", "下次见！", "拜拜，记得常来哦！"])
        
        elif "时间" in text:
            current_time = time.strftime("%H:%M", time.localtime())
            return f"现在是北京时间 {current_time}"
        
        elif "名字" in text:
            return "我叫天启，是你的智能助手！"
        
        elif "天气" in text:
            return random.choice([
                "今天天气晴朗，适合出门！",
                "天气预报说下午有雨，记得带伞",
                "气温在22-28度之间，很舒适呢"
            ])
        
        else:
            return random.choice([
                "我明白了",
                "很有趣的观点",
                "能详细说说吗？",
                "我会记住你说的话的",
                "嗯，我还在学习中..."
            ])

live2d.init()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置全局字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)
    
    pet = Pet()
    pet.show()
    
    # 显示欢迎消息
    QTimer.singleShot(1000, lambda: pet.show_bubble("你好，我是天启小助手！"))
    
    sys.exit(app.exec_())