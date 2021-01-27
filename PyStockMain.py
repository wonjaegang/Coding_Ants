import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        self.message = QTextEdit(self)
        self.accountInfo = QTextEdit(self)
        self.button1 = QPushButton("1: No-Loss Scalping", self)
        self.button1.clicked.connect(self.nolossScalping)

        self.setGUI()
        self.openLoginWindow()

    def setGUI(self):
        self.setWindowTitle("Coding Ants - Auto stock investing program")
        self.setGeometry(300, 300, 600, 330)
        label_message = QLabel("Message", self)
        label_message.move(40, 20)
        self.message.setGeometry(30, 50, 300, 100)
        self.message.setEnabled(False)
        label_accountInfo = QLabel("Account Info", self)
        label_accountInfo.move(40, 170)
        self.accountInfo.setGeometry(30, 200, 300, 100)
        self.accountInfo.setEnabled(False)
        self.button1.setGeometry(400, 50, 150, 30)

    def openLoginWindow(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.loginDone)

    def loginDone(self):
        self.message.append("Login Succeed")

    def nolossScalping(self):
        self.message.append("Algorithm Started : No Loss Scalping ")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
