import sys
from PyQt5.QtWidgets import *


# Making PyQt5 instance
mywindow = QApplication(sys.argv)
label1 = QLabel("Sentence")

label1.show()

mywindow.exec_()
