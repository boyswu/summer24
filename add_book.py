import queue
import threading
import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog
import os
from add_UI import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui
import pymysql


class recognize_figure(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(recognize_figure, self).__init__(parent)

        self.setupUi(self)

        self.pushButton.clicked.connect(self.book_infromation)


    def book_infromation(self):

        bookname = self.bookname.text()
        bookid = self.bookid.text()
        self.connect_sql(bookname, bookid)

    def connect_sql(self, bookname, bookid):
        try:
            db = pymysql.connect(host='8.147.233.239', user='root', passwd='team2111', db='wjh', charset='utf8')
        except pymysql.Error as e:
            print(f"数据库连接失败: {e}")
            return

        cursor = db.cursor()
        sql = "INSERT INTO library (bookname, bookid) VALUES (%s, %s)"
        try:
            cursor.execute(sql, (bookname, bookid))
            db.commit()
            print("数据插入成功")
            self.textEdit.append("数据插入成功")
            self.textEdit.append(f"书名: {bookname}, 书号: {bookid}")
        except pymysql.Error as e:
            db.rollback()
            print(f"数据插入失败: {e}")
            self.textEdit.append("数据插入失败")
            self.textEdit.append(f"书名: {bookname}, 书号: {bookid}")
        finally:
            db.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = recognize_figure()
    MainWindow.show()
    sys.exit(app.exec_())
