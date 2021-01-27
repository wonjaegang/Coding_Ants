import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        # GUI
        self.message = QTextEdit(self)
        self.accountInfo = QTextEdit(self)
        self.button1 = QPushButton("1: Loss Cut Scalping", self)
        self.button1.clicked.connect(self.losscutScalping)
        self.button1_Stop = QPushButton("Stop Running", self)
        self.button1_Stop.clicked.connect(self.losscutScalping_Stop)

        self.setGUI()
        self.openLoginWindow()

    def setGUI(self):
        self.setWindowTitle("Coding Ants - Auto stock investing program")
        self.setGeometry(300, 300, 650, 330)
        label_message = QLabel("Message", self)
        label_message.move(40, 20)
        self.message.setGeometry(30, 50, 300, 100)
        self.message.setEnabled(False)
        label_accountInfo = QLabel("Account Info", self)
        label_accountInfo.move(40, 170)
        self.accountInfo.setGeometry(30, 200, 300, 100)
        self.accountInfo.setEnabled(False)
        self.button1.setGeometry(350, 50, 140, 30)
        self.button1_Stop.setGeometry(520, 50, 80, 30)
        self.button1_Stop.setEnabled(False)

    def openLoginWindow(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.loginDone)

    def loginDone(self):
        self.message.append("Login Succeed")

    def losscutScalping(self):
        self.message.append("Algorithm Started : Loss Cut Scalping ")
        btn_enable_switch(self.button1_Stop, self.button1)

    def losscutScalping_Stop(self):
        self.message.append("Algorithm Stopped : Loss Cut Scalping ")
        btn_enable_switch(self.button1, self.button1_Stop)


def btn_enable_switch(btn1, btn2):
    btn1.setEnabled(True)
    btn2.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
