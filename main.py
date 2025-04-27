from windows.casual_win import ChatWindow
import sys
from PyQt5.QtWidgets import QApplication

app = QApplication(sys.argv)
window = ChatWindow()
window.show()
sys.exit(app.exec_())