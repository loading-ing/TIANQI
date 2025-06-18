import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QStackedWidget, QSystemTrayIcon, QMenu
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

# 导入每个独立的页面
from .pages.ai_chat_page_copy import AIChatPage
from .pages.voice_chat_page import VoiceChatPage
from .pages.image_text_page import ImageTextPage
from .pages.rag_page_copy import RagPage
from .pages.desktop_control_page import DesktopControlPage
from .pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("天启")
        self.setWindowIcon(QIcon("icon.png"))
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()
        self.init_menu()
        self.init_tray()

    def init_ui(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 页面实例
        self.pages = {
            "AI对话": AIChatPage(),
            # "语音对话": VoiceChatPage(),
            # "图文转换": ImageTextPage(),
            "RAG检索": RagPage(),
            # "桌面控制": DesktopControlPage(),
            # "设置": SettingsPage(),
        }

        for page in self.pages.values():
            self.stacked_widget.addWidget(page)

    def init_menu(self):
        menu_bar = self.menuBar()
        for i, name in enumerate(self.pages.keys()):
            action = QAction(name, self)
            action.triggered.connect(lambda checked, index=i: self.switch_page(index))
            menu_bar.addAction(action)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        menu_bar.addAction(exit_action)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        self.tray_icon.setToolTip("AI多功能助手")

        tray_menu = QMenu()
        restore_action = QAction("打开主界面", self)
        quit_action = QAction("退出", self)

        restore_action.triggered.connect(self.show_normal)
        quit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    # def closeEvent(self, event):
    #     event.ignore()
    #     self.hide()
    #     self.tray_icon.showMessage(
    #         "AI多功能助手",
    #         "程序已最小化到任务栏",
    #         QSystemTrayIcon.Information,
    #         2000
    #     )

    def show_normal(self):
        self.showNormal()
        self.activateWindow()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
