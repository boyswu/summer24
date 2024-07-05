from new_page import Ui_Window
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow

class SecondWindow(QMainWindow, Ui_Window):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.setupUi(self)
