import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *

# 손재균 하이요
# 소연-하이!


# 자동매수/매도 알고리즘 클래스
class TradingAlgorithm:
    def __init__(self):
        self.dealingItems = {}
        self.holdingItems = {}
        self.soldItems = {}
        self.profit = 0

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

        self.KH_Scalping = TradingAlgorithm()
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
        self.OnReceiveChejanData.connect(self.receiveChejanData)

    # 손해를 최소화하며 단기매수/매도하는 알고리즘
    def lossCutScalping(self):
        pass

    # 급등 후 매도세가 약한 종목들을 포착하여 구매하는 알고리즘
    def soaredWeakSelling(self):
        self.sendCondition("000", "0000", False)
        pass

    # 전일종가대비 10%이상 급등한 종목들을 이용해 단기매수/매도하는 알고리즘
    def KyunghoScalping(self):
        # 조건검색을 사용해 종목들을 dealingItem 에 저장
        self.sendCondition("002", "0000", False)
        self.searchLoop = QEventLoop()
        self.searchLoop.exec()

        # 초기매수 - 체결성공시 holdingItem 에 저장됨
        for code in self.KH_Scalping.dealingItems:
            self.send_order("KyunghoScalping_initial_order", "0000", "신규매수", code, 1, "시장가", 0)
            waitForMilliSec(200)

        waitForMilliSec(5000)

        # 보유종목들의 실시간 가격확인 및 매도
        # API 의 실시간조회 메서드를 사용하지 않음. 사용하는 것으로 추후에 변경해야함.
        for i in range(500):
            print("Loop %d" % i)
            print("Current Holding Items:", list(self.KH_Scalping.holdingItems.keys()))

            for code in self.KH_Scalping.holdingItems:
                self.getPriceData(code, todayString())
                self.KH_Scalping.holdingItems[code].update(self.priceDataDic.copy())
                print(code, end=': ')
                print(self.KH_Scalping.holdingItems[code])
                profit = self.KH_Scalping.holdingItems[code]["현재가"] - self.KH_Scalping.holdingItems[code]["매수가"]
                if -10 > profit or profit > 10:
                    self.send_order("KyunghoScalping_selling_order", "0000", "신규매도", code, 1, "시장가", 0)
                    waitForMilliSec(400)
                else:
                    waitForMilliSec(200)

            for code in self.KH_Scalping.soldItems:
                if code in self.KH_Scalping.holdingItems:
                    del self.KH_Scalping.holdingItems[code]

            print("\nCurrent Profit: %d\n" % self.KH_Scalping.profit)
            print("=" * 50)
            waitForMilliSec(10000)

            # 보유종목들을 모두 매도하면 알고리즘 종료
            # 알고리즘 종료시 여기서 계속 걸려서 오류남. 확인필요.
            if not list(self.KH_Scalping.holdingItems.keys()):
                print("\nTotal Profit: %d" % self.KH_Scalping.profit)
                for code in self.KH_Scalping.soldItems:
                    print("종목코드: %s  - 수익: %d" % (code, self.KH_Scalping.soldItems[code]["수익"]))
                print("\nAlgorithm Over.")
                return 0

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
                self.KH_Scalping.dealingItems[code] = {}
                mainWindow.accountInfo.append(code)
            self.searchLoop.exit()

    def receiveRealTimeSearchResult(self, code, insertDelete, conditionName, index):
        # if index == "002":
        #     if insertDelete == "I":
        #         self.KH_Scalping.dealingItems.append(code)
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

    def receiveChejanData(self, dataType, itemCount, FIDList):
        itemName = self.GetChejanData(302)
        code = self.GetChejanData(9001)[1:]
        orderType = self.GetChejanData(905)[1:]
        orderState = self.GetChejanData(913)
        orderQuantity = self.GetChejanData(900)
        fillPrice = self.GetChejanData(910)

        # KH_Scalping - 매수/매도시 holdingItem 에 추가/제거
        if code in self.KH_Scalping.dealingItems:
            if orderType == "매수":
                if orderState == "체결":
                    self.KH_Scalping.holdingItems[code] = {"매수가": int(fillPrice), "수량": orderQuantity}
            if orderType == "매도":
                if orderState == "접수":
                    self.KH_Scalping.soldItems[code] = {"수익": 0}
                if orderState == "체결":
                    gain = int(fillPrice) - self.KH_Scalping.holdingItems[code]["매수가"]
                    self.KH_Scalping.soldItems[code]["수익"] += gain
                    self.KH_Scalping.profit += gain

        # 접수 & 체결 데이터
        if dataType == "0":
            print("-" * 50)
            print("접수 / 체결")
            print("주문번호:", self.GetChejanData(9203))
            print("종목명:", itemName)
            print("종목코드:", code)
            print("주문구분:", orderType)
            print("주문상태:", orderState)
            print("주문수량:", orderQuantity)
            print("주문가격:", fillPrice)
            print("-" * 50)
        # 잔고 데이터
        if dataType == "1":
            print("-" * 50)
            print("잔고")
            print("종목명:", itemName)
            print("종목코드:", code)
            print("보유수량:", self.GetChejanData(930))
            print("-" * 50)

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
        self.requestData("getPriceData", "opt10081", "0001")
        self.requestLoop = QEventLoop()
        self.requestLoop.exec()

    def requestData(self, requestName, TrCode, screenNo):
        PreNext = 0
        self.dynamicCall("CommRqData(QString, QString, int, QString)", requestName, TrCode, PreNext, screenNo)

    def send_order(self, requestName, screenNo, orderType, code, quantity, priceType, price):
        if orderType == "신규매수":
            orderTypeInt = 1
        elif orderType == "신규매도":
            orderTypeInt = 2
        elif orderType == "매수취소":
            orderTypeInt = 3
        elif orderType == "매도취소":
            orderTypeInt = 4
        elif orderType == "매수정정":
            orderTypeInt = 5
        elif orderType == "매도정정":
            orderTypeInt = 6
        else:
            print("Error: Send_order() - Order type")
            orderTypeInt = 0

        if priceType == "시장가":
            priceTypeInt = "03"
            price = 0
        elif priceType == "지정가":
            priceTypeInt = "00"
        else:
            print("Error: Send_order() - Price type")
            priceTypeInt = ""
        accountNo = self.accountNo
        orderNo = ""
        isRequest = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                     [requestName, screenNo, accountNo, orderTypeInt, code, quantity, price,
                                      priceTypeInt, orderNo])
        if isRequest:
            mainWindow.message.append("Error: Order Dismissed : %s" % code)


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
