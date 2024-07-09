"""
用户端人脸登录系统

"""
import qdarkstyle

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication

from ui.main_UI import Ui_MainWindow

from PyQt5 import QtWidgets

from face import face_MainWindow

from register import register_MainWindow


class main_MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.face_MainWindow = face_MainWindow()  # 用户界面
        self.register_Window = register_MainWindow()  # 注册界面

        self.setWindowTitle("用户端图书借阅系统")

        self.log_in.clicked.connect(self.new_page)  # 登录按钮
        self.log_out.clicked.connect(self.log_out_system)  # 
        self.register_Button.clicked.connect(self.register_system)  # 人脸识别按钮

    def new_page(self):
        # 打开子界面
        self.hide()  # 隐藏当前界面
        self.face_MainWindow.show()
        self.face_MainWindow.log_out.clicked.connect(self.close_page)

    def close_page(self):
        # 关闭子界面
        self.face_MainWindow.close()
        self.show()  # 显示当前界面

    def register_system(self):
        # 打开注册界面
        self.hide()  # 隐藏当前界面
        self.register_Window.show()
        self.register_Window.log_out.clicked.connect(self.close_register)

    def close_register(self):
        # 关闭注册界面
        self.register_Window.close()
        self.show()  # 显示当前界面

    def log_out_system(self):
        self.face_MainWindow.close_camera()
        # 关闭窗口
        self.close()


if __name__ == "__main__":
    import sys

    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QtWidgets.QApplication(sys.argv)
    # 使用 qdarkstyle
    #
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.setStyleSheet("#MainWindow{border-image:url(./ui/1.jpg)}")
    MainWindow = main_MainWindow()
    MainWindow.show()

    sys.exit(app.exec_())
