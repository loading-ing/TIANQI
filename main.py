# from windows.main import MainWindow
from windows.live2d.main_pyqt5 import Pet as MainWindow
import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())