import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *


# 자동매수/매도 알고리즘 클래스
class TradingAlgorithm:
    def __init__(self):
        self.dealingItems = {}

    def buyingOffer(self):
        pass

    def sellingOffer(self):
        pass


# 키움 open API 관련 메서드들을 처리하는 클래스
class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__("KHOPENAPI.KHOpenAPICtrl.1")
        self.searchConditions = {}
        self.priceDataDic = {}
        self.setSignalSlot()

        self.KHScalping = TradingAlgorithm()
        self.Soared_WS = TradingAlgorithm()

        self.login()
        self.loginLoop = QEventLoop()
        self.loginLoop.exec()
        self.accountNo = self.getAccountNo()
        self.saveSearchConditions()

    # 이벤트와 그에 따른 이벤트 처리 메서드
    def setSignalSlot(self):
        self.OnEventConnect.connect(self.loginDone)
        self.OnReceiveConditionVer.connect(self.conditionSaved)
        self.OnReceiveTrCondition.connect(self.receiveSearchResult)
        self.OnReceiveRealCondition.connect(self.receiveRealTimeSearchResult)
        self.OnReceiveTrData.connect(self.receiveTrData)

    # 손해를 최소화하며 단기매수/매도하는 알고리즘
    def lossCutScalping(self):
        pass

    # 급등 후 매도세가 약한 종목들을 포착하여 구매하는 알고리즘
    def soaredWeakSelling(self):
        self.sendCondition("000", "0000", False)
        pass

    # 전일종가대비 10%이상 급등한 종목들을 이용해 단기매수/매도하는 알고리즘
    def KyunghoScalping(self):
        self.sendCondition("002", "0000", False)
        self.searchLoop = QEventLoop()
        self.searchLoop.exec()
        for code in self.KHScalping.dealingItems:
            self.getPriceData(code, todayString())
            self.KHScalping.dealingItems[code] = self.priceDataDic
            print("%s: Data loading completed" % code)
            waitForMilliSec(200)
        for dic in self.KHScalping.dealingItems:
            print(dic, end=': ')
            print(self.KHScalping.dealingItems[dic])
        pass

    # ==== 조회요청 후 수신 이벤트처리 메서드 ==============================================================================

    def receiveSearchResult(self, screenNo, codeList, conditionName, index_int, Next_int):
        if conditionName == self.searchConditions["000"]:
            resultList = codeList.split(';')
            resultList.pop()
            for code in resultList:
                self.Soared_WS.dealingItems[code] = {}
                mainWindow.accountInfo.append(code)

        if conditionName == self.searchConditions["002"]:
            resultList = codeList.split(';')
            resultList.pop()
            for code in resultList:
                self.KHScalping.dealingItems[code] = {}
                mainWindow.accountInfo.append(code)
            self.searchLoop.exit()

    def receiveRealTimeSearchResult(self, code, insertDelete, conditionName, index):
        # if index == "002":
        #     if insertDelete == "I":
        #         self.KHScalping.dealingItems.append(code)
        #         mainWindow.accountInfo.append(code)
        pass

    def receiveTrData(self, screenNo, requestName, TrCode, recordName, PreNext, _0, _1, _2, _3):
        if requestName == "getPriceData":
            self.priceDataDic.clear()
            dataNameList = ["현재가", "거래량", "시가"]
            for dataName in dataNameList:
                data = self.GetCommData(TrCode, requestName, 0, dataName)
                self.priceDataDic[dataName] = int(data)
            self.requestLoop.exit()

    # ==================================================================================================================

    def login(self):
        self.dynamicCall("CommConnect()")

    def loginDone(self):
        self.loginLoop.exit()

    def getAccountNo(self):
        string = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        accountNo = string.split(';')
        accountNo.pop()
        return accountNo[0]

    def saveSearchConditions(self):
        self.dynamicCall("GetConditionLoad()")

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

    def sendCondition(self, index, screenNo, realTime):
        isRequest = self.dynamicCall("SendCondition(QString, QString, int, int)",
                                     screenNo, self.searchConditions[index], index, realTime)
        if not isRequest:
            mainWindow.message.append("Error: Failed to request condition-searching")

    # 해당 종목/날짜의 가격데이터(현재가, 거래량, 시가)를 클래스의 priceDataDic 에 저장한다.
    # e.g. {"현재가": 15030, "거래량": 382891, "시가": 15120}
    def getPriceData(self, code, date):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        self.requestData("getPriceData", "opt10081", "0000")
        self.requestLoop = QEventLoop()
        self.requestLoop.exec()

    def requestData(self, requestName, TrCode, screenNo):
        PreNext = 0
        self.dynamicCall("CommRqData(QString, QString, int, QString)", requestName, TrCode, PreNext, screenNo)

    def send_order(self, requestName, screenNo, orderType, code, quantity, price):
        accountNo = self.accountNo
        priceType = "03"  # 시장가
        orderNo = ""
        isRequest = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                     [requestName, screenNo, accountNo, orderType, code, quantity, price, priceType,
                                      orderNo])
        if not isRequest:
            mainWindow.message.append("Error: Order Dismissed")


# 메인 GUI 창 클래스
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

    # GUI 배치관련 코드
    def setGUI(self):
        self.setWindowTitle("Coding Ants - Auto stock investing program")
        self.setGeometry(300, 300, 650, 750)
        label_message = QLabel("Message", self)
        label_message.move(40, 20)
        self.message.setGeometry(30, 50, 300, 100)
        self.message.setEnabled(False)
        label_accountInfo = QLabel("Account Info", self)
        label_accountInfo.move(40, 170)
        label_algorithms = QLabel("Algorithms", self)
        label_algorithms.move(350, 20)
        self.accountInfo.setGeometry(30, 200, 300, 500)
        self.accountInfo.setEnabled(False)
        self.button1.setGeometry(350, 50, 160, 30)
        self.button1_Stop.setGeometry(520, 50, 100, 30)
        self.button1_Stop.setEnabled(False)
        self.button2.setGeometry(350, 100, 160, 30)
        self.button3.setGeometry(350, 150, 160, 30)
        self.button3_Stop.setGeometry(520, 150, 100, 30)
        self.button3_Stop.setEnabled(False)

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


def waitForMilliSec(milliSec):
    loop = QEventLoop()
    QTimer.singleShot(milliSec, loop.quit)
    loop.exec_()


def todayString():
    nowDate = QDate.currentDate()
    today = "%04d%02d%02d" % (nowDate.year(), nowDate.month(), nowDate.day())
    return today


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec_()
