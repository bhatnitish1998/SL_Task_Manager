import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget,QWidget, QApplication
from PyQt6 import uic

class Window(QWidget):
    def __init__(self):
        super().__init__()

        uic.loadUi("basic_window.ui",self)
        self.setWindowIcon(QIcon("../Media/icon.png"))



app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
