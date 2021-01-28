import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.searchConditions = {}

        # GUI
        self.message = QTextEdit(self)
        self.accountInfo = QTextEdit(self)
        self.button1 = QPushButton("1: Loss Cut Scalping", self)
        self.button1.clicked.connect(self.losscutScalping)
        self.button1_Stop = QPushButton("Stop Running", self)
        self.button1_Stop.clicked.connect(self.losscutScalping_Stop)
        self.button2 = QPushButton("2: Soared&WeakSelling", self)
        self.button2.clicked.connect(self.soaredNweakselling)

        self.setGUI()
        self.openLoginWindow()
        self.kiwoom.OnReceiveTrData.connect(self.receiveTrData)

    def setGUI(self):
        self.setWindowTitle("Coding Ants - Auto stock investing program")
        self.setGeometry(300, 300, 650, 750)
        label_message = QLabel("Message", self)
        label_message.move(40, 20)
        self.message.setGeometry(30, 50, 300, 100)
        self.message.setEnabled(False)
        label_accountInfo = QLabel("Account Info", self)
        label_accountInfo.move(40, 170)
        self.accountInfo.setGeometry(30, 200, 300, 500)
        self.accountInfo.setEnabled(False)
        self.button1.setGeometry(350, 50, 160, 30)
        self.button1_Stop.setGeometry(520, 50, 100, 30)
        self.button1_Stop.setEnabled(False)
        self.button2.setGeometry(350, 100, 160, 30)

    def openLoginWindow(self):
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.loginDone)

    def loginDone(self):
        self.message.append("Login Succeed")
        self.saveSearchConditions()

    def saveSearchConditions(self):
        self.kiwoom.dynamicCall("GetConditionLoad()")
        self.kiwoom.OnReceiveConditionVer.connect(self.conditionSaved)

    def conditionSaved(self, saved, _):
        if saved:
            self.message.append("Conditions for searching have been saved.")
            string = self.kiwoom.dynamicCall("GetConditionNameList()")
            split_once = string.split(';')
            split_once.pop()
            for nameIndex in split_once:
                split_twice = nameIndex.split('^')
                self.searchConditions[split_twice[0]] = split_twice[1]
            print(self.searchConditions)

    def losscutScalping(self):
        self.message.append("Algorithm Started : Loss Cut Scalping ")
        btn_enable_switch(self.button1_Stop, self.button1)
        pass

    def losscutScalping_Stop(self):
        self.message.append("Algorithm Stopped : Loss Cut Scalping ")
        btn_enable_switch(self.button1, self.button1_Stop)

    def soaredNweakselling(self):
        self.button2.setEnabled(False)

    def receiveTrData(self, screenNo, requestName, TrCode, recordName, PreNext, _0, _1, _2, _3):
        pass


def btn_enable_switch(btn1, btn2):
    btn1.setEnabled(True)
    btn2.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
