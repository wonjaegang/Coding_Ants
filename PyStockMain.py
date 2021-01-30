import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *


class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__("KHOPENAPI.KHOpenAPICtrl.1")
        self.searchConditions = {}
        self.OnReceiveTrCondition.connect(self.receiveSearchResult)
        self.OnReceiveTrData.connect(self.receiveTrData)

        self.login()

    def lossCutScalping(self):
        pass

    def soaredWeakSelling(self):
        self.sendCondition("000", "0000")
        pass

    def KyunghoScalping(self):
        self.sendCondition("002", "0001")
        pass

    def receiveSearchResult(self, screenNo, codeList, conditionName, index_int, Next_int):
        if screenNo == "0000":
            resultList = codeList.split(';')
            resultList.pop()
            for code in resultList:
                mainWindow.accountInfo.append(code)

        if screenNo == "0001":
            resultList = codeList.split(';')
            resultList.pop()
            for code in resultList:
                mainWindow.accountInfo.append(code)

    def receiveTrData(self, screenNo, requestName, TrCode, recordName, PreNext, _0, _1, _2, _3):
        pass

    def login(self):
        self.dynamicCall("CommConnect()")
        self.OnEventConnect.connect(self.loginDone)

    def loginDone(self):
        mainWindow.message.append("Login Succeed")
        self.saveSearchConditions()

    def saveSearchConditions(self):
        self.dynamicCall("GetConditionLoad()")
        self.OnReceiveConditionVer.connect(self.conditionSaved)

    def conditionSaved(self, saved, _):
        if saved:
            mainWindow.message.append("Search conditions have been saved.")
            string = self.dynamicCall("GetConditionNameList()")
            split_once = string.split(';')
            split_once.pop()
            for nameIndex in split_once:
                split_twice = nameIndex.split('^')
                self.searchConditions[split_twice[0]] = split_twice[1]
        else:
            mainWindow.message.append("Error : Failed to load search conditions")

    def sendCondition(self, index, screenNo):
        self.dynamicCall("SendCondition(QString, QString, int, int)",
                         screenNo, self.searchConditions[index], index, 0)


class TradingAlgorithm(KiwoomAPI):
    def __init__(self):
        super().__init__()
        pass

    def buyingOffer(self):
        pass

    def sellingOffer(self):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoomAPI = KiwoomAPI()

        # GUI Definitions
        self.message = QTextEdit(self)
        self.accountInfo = QTextEdit(self)
        self.button1 = QPushButton("1: Loss Cut Scalping", self)
        self.button1.clicked.connect(self.run_lossCutScalping)
        self.button1_Stop = QPushButton("Stop Running", self)
        self.button1_Stop.clicked.connect(self.stop_lossCutScalping)
        self.button2 = QPushButton("2: Soared&WeakSelling", self)
        self.button2.clicked.connect(self.run_soaredWeakSelling)
        self.button3 = QPushButton("3: Kyungho's Scalping", self)
        self.button3.clicked.connect(self.run_KyunghoScalping)
        self.button3_Stop = QPushButton("Stop Running", self)
        self.button3_Stop.clicked.connect(self.stop_KyunghoScalping)

        self.setGUI()

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
        self.button3.setGeometry(350, 150, 160, 30)
        self.button3_Stop.setGeometry(520, 150, 100, 30)

    def run_lossCutScalping(self):
        self.message.append("Algorithm Started : Loss Cut Scalping ")
        btn_switching(self.button1_Stop, self.button1)
        pass

    def stop_lossCutScalping(self):
        self.message.append("Algorithm Stopped : Loss Cut Scalping ")
        btn_switching(self.button1, self.button1_Stop)

    def run_soaredWeakSelling(self):
        self.message.append("Algorithm Started : Weak Selling Stock after soared")
        self.button2.setEnabled(False)
        self.kiwoomAPI.soaredWeakSelling()

    def run_KyunghoScalping(self):
        self.message.append("Algorithm Started : Kyungho Scalping ")
        btn_switching(self.button3_Stop, self.button3)
        self.kiwoomAPI.KyunghoScalping()

    def stop_KyunghoScalping(self):
        self.message.append("Algorithm Stopped : Kyungho Scalping ")
        btn_switching(self.button3, self.button3_Stop)


def btn_switching(btn1, btn2):
    btn1.setEnabled(True)
    btn2.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
