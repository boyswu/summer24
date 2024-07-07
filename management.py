from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from ui.management_UI import Ui_MainWindow
from PyQt5 import QtWidgets
from sql import host, user, passwd, db2
import pymysql
from new_page_connect import SecondWindow


class recognize_figure(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(recognize_figure, self).__init__(parent)
        self.result = None
        self.setupUi(self)
        self.select.clicked.connect(self.select_one_sql)
        self.insert.clicked.connect(self.insert_sql)
        self.reduce.clicked.connect(self.delete_sql)
        self.change.clicked.connect(self.update_sql)
        self.Ui_Window = SecondWindow()

    def connect_sql(self, ):
        db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
        return db

    def new_page(self):
        # 打开子界面
        self.Ui_Window.show()
        self.Ui_Window.sure.clicked.connect(self.close_page)

    def close_page(self):
        # 关闭子界面
        self.Ui_Window.close()

    def select_sql(self):
        db = self.connect_sql()
        cursor = db.cursor()
        sql = "SELECT * FROM book_info"
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            print("查询结果：", result)
            # 将查询结果插入到tableWidget里
            for row in result:
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                for i in range(len(row)):
                    self.tableWidget.setItem(self.tableWidget.rowCount() - 1, i,
                                             QtWidgets.QTableWidgetItem(str(row[i])))
        except pymysql.Error as e:
            print(f"数据库查询失败: {e}")
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText("数据库查询失败")
        finally:
            db.close()

    def select_one_sql(self):
        bookname = self.bookname.text()
        print(bookname)
        db = self.connect_sql()
        cursor = db.cursor()
        # 通过bookname或者bookid查询
        sql = "SELECT * FROM book_info WHERE bookname = %s "
        # 将查询结果覆盖到tableWidget里
        if self.bookname.text() == "" or self.bookid.text() == "":
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText("请输入书名和书号")
            return
        else:
            cursor.execute(sql, bookname)
            result = cursor.fetchone()  # 获取查询结果的第一行
            print("查询结果：", result)
            # 将查询结果到覆盖到tableWidget里
            if result is None:
                self.new_page()
                # 在label控件中显示提示信息
                self.Ui_Window.show_text.setText("没有该书")
                return
            else:
                for i in range(len(result)):
                    self.tableWidget.setItem(0, i, QtWidgets.QTableWidgetItem(str(result[i])))
                print("查询成功")
                self.new_page()
                # 在label控件中显示提示信息
                self.Ui_Window.show_text.setText(f"查询成功 书名: {result[0]}, 书号: {result[1]}")
                db.close()
                return


    def insert_sql(self):

        db = self.connect_sql()
        cursor = db.cursor()
        bookname = self.bookname.text()
        bookid = self.bookid.text()

        sql = "INSERT INTO book_info(bookname, bookid) VALUES(%s, %s)"
        if bookname == "" or bookid == "":
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText("请输入书名和书号")
            return
        try:
            cursor.execute(sql, (bookname, bookid))
            db.commit()
            print("数据插入成功")
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText(f"数据插入成功 书名: {bookname}, 书号: {bookid}")

            # 将数据插入到tableWidget里
            self.tableWidget.insertRow(self.tableWidget.rowCount())
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(bookname))
            self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QtWidgets.QTableWidgetItem(bookid))
        except pymysql.Error as e:
            print(f"数据库插入失败: {e}")
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText("数据库插入失败")
        finally:
            db.close()

    def delete_sql(self):
        db = self.connect_sql()
        cursor = db.cursor()
        # 将tableWidget里的数据提取出来，然后删除数据库里的数据
        current_row = self.tableWidget.currentRow()
        bookname_item = self.tableWidget.item(current_row, 0)
        bookid_item = self.tableWidget.item(current_row, 1)

        if bookname_item is None or bookid_item is None:
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText("将鼠标移到需要删除的书")
            return

        bookname = bookname_item.text()
        bookid = bookid_item.text()
        sql = "DELETE FROM book_info WHERE bookname = %s AND bookid = %s"
        print(f"删除书名: {bookname}, 书号: {bookid}")

        try:
            cursor.execute(sql, (bookname, bookid))
            db.commit()
            print("数据删除成功")
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText(f"数据删除成功 书名: {bookname}, 书号: {bookid}")
            # 将数据从tableWidget里删除
            self.tableWidget.removeRow(current_row)
        except pymysql.Error as e:
            print(f"数据库删除失败: {e}")
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText("数据库删除失败")
        finally:
            db.close()

    def update_sql(self):
        db = self.connect_sql()
        cursor = db.cursor()
        # 查询数据库里的所有数据，并且将数据提取出来与tableWidget里的数据进行遍历，如果一致，则不更新数据库，否则更新数据库
        # 先查询数据库里的数据
        sql = "SELECT * FROM book_info"
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            self.result = result
            print("查询结果：", result)
        except pymysql.Error as e:
            print(f"数据库查询失败: {e}")
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText("数据库查询失败")

        # 遍历tableWidget里的数据，如果一致，则不更新数据库，否则更新数据库
        # 所有更新的书名和对应的书号
        new_bookname_bookid = []
        for i in range(self.tableWidget.rowCount()):
            print(f"第{i}行数据")
            bookname = self.result[i][0]
            bookid = self.result[i][1]
            new_bookname = self.tableWidget.item(i, 0).text()
            new_bookid = self.tableWidget.item(i, 1).text()
            # print(f"数据库里的书名: {bookname}, 数据库里的书号: {bookid}")
            # print(f"tableWidget里的书名: {new_bookname}, tableWidget里的书号: {new_bookid}")

            if new_bookname == bookname and new_bookid == bookid:
                print("数据一致，不更新数据库")

            else:
                print("数据不一致，更新数据库")

                sql = "UPDATE book_info SET bookname = %s, bookid = %s WHERE bookname = %s AND bookid = %s"
                try:
                    cursor.execute(sql, (new_bookname, new_bookid, bookname, bookid))
                    db.commit()
                    new_bookname_bookid.append((new_bookname, new_bookid))
                    print("数据更新成功")

                except pymysql.Error as e:
                    print(f"数据库更新失败: {e}")
                    self.new_page()
                    # 在label控件中显示提示信息
                    self.Ui_Window.show_text.setText("数据库更新失败")


        if len(new_bookname_bookid) == 0:
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText("数据一致，不更新数据库")
        else:
            print(f"更新的书名和对应的书号: {new_bookname_bookid}")
            self.new_page()
            # 在label控件中显示提示信息
            self.Ui_Window.show_text.setText(f"数据更新成功 书名: {new_bookname_bookid}")

    # def closeEvent(self, event):
    #     reply = QtWidgets.QMessageBox.question(self, 'Message', "Are you sure to quit?",
    #                                            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
    #                                            QtWidgets.QMessageBox.No)
    #     if reply == QtWidgets.QMessageBox.Yes:
    #         event.accept()
    #     else:
    #         event.ignore()


if __name__ == "__main__":
    import sys

    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = recognize_figure()
    MainWindow.show()
    # 调用select_sql方法
    MainWindow.select_sql()

    sys.exit(app.exec_())
