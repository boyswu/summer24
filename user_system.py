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
from PyQt5 import QtGui, QtCore
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
        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect(self.select_sql)
        # self.timer.start(2000)  # 每5秒更新一次
        self.path = ""
        self.user_name = None
        self.user_id = None
        self.results = None

    def connect_sql(self):
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
            # # 读取图像
            # image = cv2.imread(self.path)
            # img = self.recognize_figure.label_img(image)
            # # 固定 QLabel 的大小
            # self.label.setFixedSize(800,300)  # 设置你希望的固定大小
            # self.label.setPixmap(QtGui.QPixmap.fromImage(img))
            return

    def transitional_information(self, results, recommend_book):
        # user_name, feature, place, user_id, sex, phone = results[0]
        user_name, _, _, user_id, _, _ = results[0]
        # print(user_name, user_id)
        self.results = results
        self.user_name = user_name
        self.user_id = user_id
        # 将推荐书籍插入到label中
        recommend = []
        for i in recommend_book:
            recommend.append(i)
            print(i)
        print("\n")
        print(recommend)
        # 将列表中的元素用换行符连接
        recommend_text = "\n".join(recommend)

        # 设置label的文本
        self.label.setText("推荐书籍：\n" + recommend_text)



    def select_sql(self):
        user_name = self.user_name

        db, cursor = self.connect_sql()
        sql = "SELECT * FROM borrowlist WHERE user_name = '{}'".format(user_name)
        try:
            # 清空表格中的所有行
            self.tableWidget.setRowCount(0)
            cursor.execute(sql)
            result = cursor.fetchall()
            # print("查询结果：", result)
            # 将查询结果插入到tableWidget里
            for row in result:
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                for i in range(len(row)):
                    self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i,
                                             QtWidgets.QTableWidgetItem(str(row[i])))
        except pymysql.Error as e:
            print(f"数据库查询失败: {e}")
            QtWidgets.QMessageBox.warning(self, "警告", f"数据库查询失败: {e}")
        finally:
            cursor.close()
            db.close()

    def borrow_book_func(self):
        if not self.path:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择一本书！")
            return
        result = self.recognize_figure.mode_match(self.path)
        if not result:
            QtWidgets.QMessageBox.warning(self, "警告", "识别失败！")
            return
        # print(result)
        user_name = self.user_name
        user_id = self.user_id
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
        SELECT br_book_time, back_book_time,renew_book FROM borrowlist  WHERE user_br_book_id = '{}' AND user_name = '{}' 
        ORDER BY back_book_time ASC   LIMIT 1""".format(result, user_name)

        # ORDER BY back_book_time DESC：按 back_book_time 列降序排列结果。LIMIT 1：限制结果集只返回一行。
        try:
            cursor.execute(sql)
            # 获取查询结果
            results = cursor.fetchall()
            if results:
                # print(results)
                # 获取应还时间
                br_book_time, back_book_time, renew_book = results[0]  # 这里0是因为只取第一行数据
                # print(f"br_book_time:{br_book_time}, back_book_time:{back_book_time}")
                # print(f"br_book_time is None: {br_book_time is None}")
                # print(f"back_book_time is None: {back_book_time is None}")

                # 如果查询结果不为空，则提示用户有借阅过该书
                # 如果查询结果为空，则提示用户没有借阅过该书
                if back_book_time is not None:
                    # 弹出提示框，确认是否借阅
                    reply = QtWidgets.QMessageBox.question(self, '提示', f'你已经借阅过{book_name}，是否要再次借阅？',
                                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                           QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.No:
                        return
                    if reply == QtWidgets.QMessageBox.Yes:

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
                            QtWidgets.QMessageBox.information(self, "提示", f"{book_name}书籍借阅成功！")
                            self.select_sql()
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
                    # 再次检测是否是续借过的书籍
                    if renew_book is not None:
                        QtWidgets.QMessageBox.warning(self, "警告", "该书已续借过,请先归还！")
                        return
                    else:
                        # 检测是否超过0.0000001天
                        now_time = datetime.datetime.now()
                        max_days = 30
                        times = datetime.timedelta(days=max_days) - (now_time - br_book_time)
                        formatted_times = str(times).split('.')[0]
                        print(formatted_times)
                        if times < datetime.timedelta(0):
                            QtWidgets.QMessageBox.warning(self, "警告", "已逾期，请先归还逾期书籍，再借阅新书！")
                            return
                        else:
                            '''
                            续借书籍
                            '''
                            # 弹出提示框，确认是否续借
                            reply = QtWidgets.QMessageBox.question(self, "提示",
                                                                   f"待归还时间还剩余{formatted_times},是否确定续借{book_name}！",
                                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                                   QtWidgets.QMessageBox.No
                                                                   )
                            if reply == QtWidgets.QMessageBox.No:
                                return
                            if reply == QtWidgets.QMessageBox.Yes:
                                renew_br_book_time = datetime.datetime.now()
                                # 获取应还时间
                                # 获取书籍对象
                                # 借阅书籍
                                sql = ("UPDATE borrowlist SET renew_br_book_time = '{}', renew_book = '{}' WHERE "
                                       "user_br_book_id = '{}' AND"
                                       " user_name = '{}'").format(renew_br_book_time, '1', result, user_name)
                                try:
                                    cursor.execute(sql)
                                    db.commit()
                                    QtWidgets.QMessageBox.information(self, "提示", f"{book_name}借阅成功！")
                                    self.select_sql()
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
                '''
                 没有借阅过该书
                '''
                # 弹出提示框，确认是否借阅
                reply = QtWidgets.QMessageBox.question(self, '提示', f'是否借阅{book_name}？',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.No:
                    return
                if reply == QtWidgets.QMessageBox.Yes:

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
                        QtWidgets.QMessageBox.information(self, "提示", f"{book_name}借阅成功！")
                        self.select_sql()
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
        # print(result)
        user_name = self.user_name
        user_id = self.user_id
        # 连接数据库
        db, cursor = self.connect_sql()
        # 查询数据表里的数据
        sql = ("SELECT br_book_time,renew_br_book_time, back_book_time,user_br_book_name FROM borrowlist WHERE "
               "user_br_book_id = '{"
               "}'AND user_name = '{}'"
               "ORDER BY back_book_time ASC  LIMIT 1").format(
            result,
            user_name)
        try:
            cursor.execute(sql)
            # 获取查询结果
            results = cursor.fetchall()
            # print(f"results: {results}")
            # print(f"results is None: {results is None}")
            # 获取应还时间
            br_book_time, renew_br_book_time, back_book_time, user_br_book_name = results[0]  # 这里0是因为只取第一行数据
            # print(f"back_book_time is None: {back_book_time is None}")
            # 如果查询结果为空，则提示用户没有借阅该书
            if not results:
                QtWidgets.QMessageBox.warning(self, "警告", "没有借阅该书！")
                return
            if back_book_time is not None:
                QtWidgets.QMessageBox.warning(self, "警告", "该书已归还！")
                return
            if back_book_time is None and renew_br_book_time is None:
                # 检测是否超过0.0000001天
                now_time = datetime.datetime.now()
                max_days = 30
                print(f'剩余时间{now_time - br_book_time}')
                times = datetime.timedelta(days=max_days) - (now_time - br_book_time)
                # print(f"times: {times}")

                # 归还书籍
                # 弹出提示框，确认是否归还
                reply = QtWidgets.QMessageBox.question(self, '提示', f'确认归还{user_br_book_name}吗？',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    if times < datetime.timedelta(0):
                        # 将days和hour转换正数
                        QtWidgets.QMessageBox.warning(self, "警告", f"已逾期{abs(times)}！,请缴纳罚款！")
                        overdue_time = str(abs(times)).split('.')[0]
                        back_book_time = datetime.datetime.now()
                        # 连接数据库
                        # 更改数据表中的数据
                        sql = "UPDATE borrowlist SET back_book_time = %s WHERE user_br_book_id = '{}' AND user_name = '{}'".format(
                            result, user_name)
                        sql_2 = ("INSERT INTO overdue_list (user_id , user_name, user_br_book_id,br_book_time,"
                                 "back_book_time,user_br_book_name,overdue_time,overdue_state) "
                                 "VALUES ('{}', '{}', '{}','{}', '{}','{}','{}','{}')").format(user_id, user_name,
                                                                                               result,
                                                                                               br_book_time,
                                                                                               back_book_time,
                                                                                               user_br_book_name,
                                                                                               overdue_time, 'no')
                        try:

                            cursor.execute(sql, back_book_time)
                            cursor.execute(sql_2)
                            db.commit()
                            QtWidgets.QMessageBox.information(self, "提示", f"{user_br_book_name}书籍归还成功！")
                            self.select_sql()
                        except Exception as e:
                            # 回滚
                            print(e)
                            db.rollback()
                            QtWidgets.QMessageBox.warning(self, "警告", "归还失败！")
                            return
                        finally:
                            cursor.close()
                            db.close()
                            return
                    else:
                        # 更改数据表中的数据
                        sql = (
                            "UPDATE borrowlist SET back_book_time = %s WHERE user_br_book_id = '{}' AND user_name = "
                            "'{}'").format(
                            result, user_name)
                        try:
                            back_book_time = datetime.datetime.now()
                            cursor.execute(sql, back_book_time)
                            db.commit()
                            QtWidgets.QMessageBox.information(self, "提示", f"{user_br_book_name}书籍归还成功！")
                            self.select_sql()
                        except Exception as e:
                            # 回滚
                            print(e)
                            db.rollback()
                            QtWidgets.QMessageBox.warning(self, "警告", "归还失败！")
                            return
                        finally:
                            cursor.close()
                            db.close()
                            return
                else:
                    return
            if back_book_time is None and renew_br_book_time is not None:
                # 检测是否超过0.0000001天
                now_time = datetime.datetime.now()
                max_days = 30
                print(f'剩余时间{now_time - br_book_time}')
                times = datetime.timedelta(days=max_days) - (now_time - br_book_time)
                # 归还书籍
                # 弹出提示框，确认是否归还
                reply = QtWidgets.QMessageBox.question(self, '提示', f'确认归还{user_br_book_name}吗？',
                                                       QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                       QtWidgets.QMessageBox.No)
                if reply == QtWidgets.QMessageBox.Yes:
                    if times < datetime.timedelta(0):
                        # 将days和hour转换正数
                        QtWidgets.QMessageBox.warning(self, "警告", f"已逾期{abs(times)}！,请缴纳罚款！")
                        overdue_time = str(times).split('.')[0]
                        back_book_time = datetime.datetime.now()
                        # 更改数据表中的数据
                        sql = ("UPDATE borrowlist SET back_book_time = %s WHERE user_br_book_id = '{}' AND user_name = "
                               "'{}'").format(
                            result, user_name)
                        sql_2 = ("INSERT INTO overdue_list (user_id , user_name, user_br_book_id,renew_br_book_time,"
                                 "back_book_time,user_br_book_name,overdue_time,overdue_state) "
                                 "VALUES ('{}', '{}', '{}','{}', '{}','{}','{}','{}')").format(user_id, user_name,
                                                                                               result,
                                                                                               renew_br_book_time,
                                                                                               back_book_time,
                                                                                               user_br_book_name,
                                                                                               overdue_time, 'no')
                        try:

                            cursor.execute(sql, back_book_time)
                            cursor.execute(sql_2)
                            db.commit()
                            QtWidgets.QMessageBox.information(self, "提示", "归还成功！")
                            self.select_sql()
                        except Exception as e:
                            # 回滚
                            print(e)
                            db.rollback()
                            QtWidgets.QMessageBox.warning(self, "警告", "归还失败！")
                            return
                        finally:
                            cursor.close()
                            db.close()
                            return
                    else:
                        # 更改数据表中的数据
                        sql = ("UPDATE borrowlist SET back_book_time = %s WHERE user_br_book_id = '{}' AND user_name = "
                               "'{}'").format(
                            result, user_name)
                        try:
                            back_book_time = datetime.datetime.now()
                            cursor.execute(sql, back_book_time)
                            db.commit()
                            QtWidgets.QMessageBox.information(self, "提示", f"{user_br_book_name}书籍归还成功！")
                            self.select_sql()
                        except Exception as e:
                            # 回滚
                            print(e)
                            db.rollback()
                            QtWidgets.QMessageBox.warning(self, "警告", "归还失败！")
                            return
                        finally:
                            cursor.close()
                            db.close()
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
        # finally:
        #     cursor.close()
        #     db.close()
        #     return


if __name__ == "__main__":
    import sys

    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QtWidgets.QApplication(sys.argv)
    # 使用 qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = UserMainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
