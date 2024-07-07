"""
用户端图书借阅

"""
import os

from PyQt5.QtWidgets import QFileDialog

import qdarkstyle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from ui.user_UI import Ui_MainWindow
from PyQt5 import QtWidgets
import pymysql

import cv2
from PyQt5 import QtGui
from recognize_opencv_three import recognize_figure
from sql import host, user, passwd, db2
import datetime


class UserMainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("用户端图书借阅系统")
        self.cwd = os.getcwd()  # 获取当前程序文件位置

        self.label.setScaledContents(True)  # 图片自适应大小

        self.select_book.clicked.connect(self.open_file)
        #
        self.borrow_book.clicked.connect(self.borrow_book_func)

        self.return_book.clicked.connect(self.return_book_func)

        self.recognize_figure = recognize_figure()
        self.path = ""

    def connect_sql(self, ):
        # 连接数据库
        db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
        cursor = db.cursor()
        return db, cursor

    def open_file(self):
        path = QFileDialog.getOpenFileName(self,
                                           "选取文件",
                                           self.cwd,  # 起始路径
                                           "Image Files (*.jpg *.png *.jpeg *.bmp)")  # 设置文件扩展名过滤,用双分号间隔
        if path == "":
            print("取消选择")
            return
        else:
            print("\n你选择的文件夹为:", path)
            self.path = path[0]
            # 读取图像
            image = cv2.imread(self.path)

            img = self.recognize_figure.label_img(image)
            # 固定 QLabel 的大小
            self.label.setFixedSize(800, 400)  # 设置你希望的固定大小
            self.label.setPixmap(QtGui.QPixmap.fromImage(img))
            return

    def borrow_book_func(self):
        if not self.path:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择一本书！")
            return
        result = self.recognize_figure.mode_match(self.path)
        if not result:
            QtWidgets.QMessageBox.warning(self, "警告", "识别失败！")
            return
        print(result)
        user_name = "user1"
        # 连接数据库
        db, cursor = self.connect_sql()
        # 连接数据库
        sql = "SELECT book_name, book_cm_isbn FROM book_info WHERE book_cm_isbn = %s"
        try:
            cursor.execute(sql, result)
            # 获取查询结果
            # 如果查询结果为空，则提示用户没有该书
            results = cursor.fetchall()
            if results:
                book_name, book_id = results[0]
                print(book_name, book_id)
            else:
                QtWidgets.QMessageBox.warning(self, "警告", "没有该书！")
                return

        except Exception as e:
            # 回滚
            print(e)
            db.rollback()
            QtWidgets.QMessageBox.warning(self, "警告", f"查询书籍时出错: {e}")
            return
        # 查询用户是否有借阅过该书未归还的书籍
        sql = """
        SELECT br_book_time, back_book_time FROM borrowlist  WHERE user_br_book_id = '{}' AND user_name = '{}' 
        ORDER BY back_book_time ASC   LIMIT 1""".format(result, user_name)

        # ORDER BY back_book_time DESC：按 back_book_time 列降序排列结果。LIMIT 1：限制结果集只返回一行。
        try:
            cursor.execute(sql)
            # 获取查询结果
            results = cursor.fetchall()
            if results:
                print(results)
                # 获取应还时间
                br_book_time, back_book_time = results[0]  # 这里0是因为只取第一行数据
                print(f"br_book_time:{br_book_time}, back_book_time:{back_book_time}")
                print(f"br_book_time is None: {br_book_time is None}")
                print(f"back_book_time is None: {back_book_time is None}")

                # 如果查询结果不为空，则提示用户有借阅过该书
                # 如果查询结果为空，则提示用户没有借阅过该书
                if back_book_time is not None:
                    # 弹出提示框，确认是否借阅
                    reply = QtWidgets.QMessageBox.question(self, '提示', '确认借阅吗？',
                                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                           QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.No:
                        return
                    if reply == QtWidgets.QMessageBox.Yes:
                        user_id = 1
                        # # 获取用户名
                        # user_name = "user1"
                        # 获取书名
                        # bookname = results[0][0]
                        # print(" bookname", bookname)
                        # # 获取书籍id
                        # book_id = results[0][2]
                        # print(" book_id", book_id)
                        book_object = "文学"
                        br_book_time = datetime.datetime.now()
                        # 获取应还时间
                        # 获取书籍对象
                        # 借阅书籍
                        sql = ("INSERT INTO borrowlist (user_id, user_name, user_br_book_id, br_book_time,"
                               "user_br_book_name,book_object)"
                               " VALUES ('{}', '{}', '{}','{}', '{}','{}')").format(user_id, user_name,
                                                                                    book_id, br_book_time,
                                                                                    book_name, book_object)
                        try:
                            cursor.execute(sql)
                            db.commit()
                            QtWidgets.QMessageBox.information(self, "提示", "借阅成功！")
                        except Exception as e:
                            # 回滚
                            print(e)
                            db.rollback()
                            QtWidgets.QMessageBox.warning(self, "警告", "借阅失败！")
                        # 关闭数据库连接
                        finally:
                            cursor.close()
                            db.close()
                            return
                else:
                    QtWidgets.QMessageBox.warning(self, "警告", "该书已借阅,请先归还后再借阅！")
                    return
            else:
                # 弹出提示框，确认是否借阅
                reply = QtWidgets.QMessageBox.question(self, '提示', '确认借阅吗？',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.No:
                    return
                if reply == QtWidgets.QMessageBox.Yes:
                    user_id = 1
                    # # 获取用户名
                    # user_name = "user1"
                    # # 获取书名
                    # bookname = results
                    # print(" bookname", bookname)
                    # # 获取书籍id
                    # book_id = results
                    # print(" book_id", book_id)
                    book_object = "文学"
                    br_book_time = datetime.datetime.now()
                    # 获取应还时间
                    # 获取书籍对象
                    # 借阅书籍
                    sql = ("INSERT INTO borrowlist (user_id, user_name, user_br_book_id, br_book_time,"
                           "user_br_book_name,book_object)"
                           " VALUES ('{}', '{}', '{}','{}', '{}','{}')").format(user_id, user_name,
                                                                                book_id, br_book_time,
                                                                                book_name, book_object)
                    try:
                        cursor.execute(sql)
                        db.commit()
                        QtWidgets.QMessageBox.information(self, "提示", "借阅成功！")
                    except Exception as e:
                        # 回滚
                        print(e)
                        db.rollback()
                        QtWidgets.QMessageBox.warning(self, "警告", "借阅失败！")
                    # 关闭数据库连接
                    finally:
                        cursor.close()
                        db.close()
                        return
        except Exception as e:
            # 回滚
            print(e)
            db.rollback()
            QtWidgets.QMessageBox.warning(self, "警告", "借阅失败！")
            # 关闭数据库连接
        # finally:
        #     cursor.close()
        #     db.close()
        #     return

    def return_book_func(self):
        if not self.path:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择一本书！")
            return
        result = self.recognize_figure.mode_match(self.path)
        if not result:
            QtWidgets.QMessageBox.warning(self, "警告", "识别失败！")
            return
        print(result)
        user_name = "user1"
        # 连接数据库
        db, cursor = self.connect_sql()
        # 查询数据表里的数据
        sql = ("SELECT br_book_time, back_book_time FROM borrowlist WHERE user_br_book_id = '{}'AND user_name = '{}' "
               "ORDER BY back_book_time ASC  LIMIT 1").format(
            result,
            user_name)
        try:
            cursor.execute(sql)
            # 获取查询结果
            results = cursor.fetchall()
            print(f"results: {results}")
            print(f"results is None: {results is None}")
            # 获取应还时间
            br_book_time, back_book_time = results[0]  # 这里0是因为只取第一行数据
            print(f"back_book_time is None: {back_book_time is None}")
            # 如果查询结果为空，则提示用户没有借阅该书
            if not results:
                QtWidgets.QMessageBox.warning(self, "警告", "没有借阅该书！")
                return
            if back_book_time is not None:
                QtWidgets.QMessageBox.warning(self, "警告", "该书已归还！")
                return
            if back_book_time is None:
                # 归还书籍
                # 弹出提示框，确认是否归还
                reply = QtWidgets.QMessageBox.question(self, '提示', '确认归还吗？',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    # 连接数据库
                    db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
                    cursor = db.cursor()
                    # 更改数据表中的数据
                    sql = "UPDATE borrowlist SET back_book_time = %s WHERE user_br_book_id = '{}' AND user_name = '{}'".format(
                        result, user_name)
                    try:

                        back_book_time = datetime.datetime.now()
                        cursor.execute(sql, back_book_time)
                        db.commit()
                        QtWidgets.QMessageBox.information(self, "提示", "归还成功！")
                    except Exception as e:
                        # 回滚
                        print(e)
                        db.rollback()
                        QtWidgets.QMessageBox.warning(self, "警告", "归还失败！")
                        return
                else:
                    return
        except Exception as e:
            # 回滚
            print(e)
            db.rollback()
            QtWidgets.QMessageBox.warning(self, "警告", "归还失败!!")
            return
            # 关闭数据库连接
        finally:
            cursor.close()
            db.close()
            return

if __name__ == "__main__":
    import sys

    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication(sys.argv)
    # 使用 qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = UserMainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
