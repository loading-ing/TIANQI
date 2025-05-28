import live2d.v3 as live2d

from PyQt5.Qt import QCursor, Qt
from PyQt5.QtWidgets import QOpenGLWidget

from windows.main import MainWindow
from example.manager import manager

import os

class Pet(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("天启")
        self.setFixedSize(400, 400)
        self.management_window = None
        self.pet_model: live2d.LAppModel | None = None

    def timerEvent(self, a0):
        x, y = QCursor.pos().x() - self.x(), QCursor.pos().y() - self.y()
        self.pet_model.Drag(x, y)

        self.update()

    def initializeGL(self):
        live2d.glewInit()
        self.pet_model = live2d.LAppModel()
        self.pet_model.LoadModelJson("resources/live2d/v3/nn/nn.model3.json")
        self.startTimer(1)

    def resizeGL(self, w, h):
        self.pet_model.Resize(w, h)

    def paintGL(self):
        live2d.clearBuffer()
        self.pet_model.Update()
        self.pet_model.Draw()
    
    def mousePressEvent(self, event):
        # 判断鼠标点击事件
        if event.button() == Qt.LeftButton:
            print("左键点击：启动语音对话")
            self.start_voice_chat()
        elif event.button() == Qt.RightButton:
            print("右键点击：打开管理界面")
            self.open_management_ui()
        else:
            super().mousePressEvent(event)

    def start_voice_chat(self):
        """
        TODO：这里写调用语音对话的逻辑
        """
        print("这里调用语音对话逻辑")


    def open_management_ui(self):
        """
        右键点击，弹出管理界面（MainWindow）
        """
        if self.management_window is None:
            self.management_window = MainWindow()
        self.management_window.show()
        self.management_window.raise_()  # 确保窗口在最前面
        self.management_window.activateWindow()  # 激活窗口



live2d.init()
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QCoreApplication, Qt

    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = Pet()
    window.show()
    sys.exit(app.exec_())