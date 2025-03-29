#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QLineEdit, QInputDialog


class Demo(QWidget):
    def __init__(self):
        super(Demo, self).__init__()
        self.initUI()

    def initUI(self):

        okButton = QPushButton('OK')
        cancelButton = QPushButton('Cancel')
        responseLine = QLineEdit("response")
        inputLine = QLineEdit("input")

        responseVBox = QVBoxLayout()
        responseVBox.addWidget(responseLine)
        inputVBox = QVBoxLayout()
        inputHBox = QHBoxLayout()
        inputHBox.addWidget(inputLine)
        inputHBox.addWidget(okButton)
        inputVBox.addLayout(inputHBox)

        mainVBox = QVBoxLayout()
        mainVBox.addLayout(responseVBox)
        mainVBox.addLayout(inputVBox)

        self.setLayout(mainVBox)
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('QHBoxLayout and QVBoxLayout')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = Demo()
    sys.exit(app.exec_())
