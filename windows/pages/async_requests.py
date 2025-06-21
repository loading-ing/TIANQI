import sys
import aiohttp
import asyncio
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt


class StreamWorker(QThread):
    update_text = pyqtSignal(str)
    stream_done = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    async def fetch_stream(self, prompt):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post("http://127.0.0.1:8000/rag/chat/",json={"query":prompt,"k":5}) as resp:
                    if resp.status != 200:
                        self.error.emit(f"HTTP error {resp.status}")
                        return
                    async for line in resp.content:
                        line = line.decode("utf-8").strip()
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
                        if mode == "context":
                            # self.context_box.setPlainText(content)
                            self.update_text.emit(content)
                        elif mode == "token":
                            content = content[len("event: token data: "):]
                            # self.output_box.append(content)
                            self.update_text.emit(content)
        except Exception as e:
            self.error.emit(str(e))

        self.stream_done.emit()

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.fetch_stream(self.prompt))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("大模型流式输出演示")
        self.setGeometry(200, 200, 500, 400)

        self.layout = QVBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("请输入你的 prompt...")
        self.layout.addWidget(self.input)

        self.button = QPushButton("提交")
        self.button.clicked.connect(self.on_submit)
        self.layout.addWidget(self.button)

        self.loading_label = QLabel("🤖 正在生成中...")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        self.layout.addWidget(self.loading_label)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.setLayout(self.layout)

    def on_submit(self):
        prompt = self.input.text().strip()
        if not prompt:
            self.output.setPlainText("⚠️ 请输入 prompt")
            return

        self.output.clear()
        self.loading_label.show()
        self.button.setDisabled(True)

        self.worker = StreamWorker(prompt)
        self.worker.update_text.connect(self.append_output)
        self.worker.stream_done.connect(self.on_done)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def append_output(self, chunk):
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(chunk)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def on_done(self):
        self.loading_label.hide()
        self.button.setDisabled(False)

    def on_error(self, msg):
        self.output.append(f"❌ 错误: {msg}")
        self.loading_label.hide()
        self.button.setDisabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
