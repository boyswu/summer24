from add_UI import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui
from sql import host, user, passwd, db2
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
            db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
        except pymysql.Error as e:
            print(f"数据库连接失败: {e}")
            return
        sql = "SELECT * FROM library WHERE bookname = %s AND bookid = %s"
        try:
            cursor = db.cursor()
            cursor.execute(sql, (bookname, bookid))
            result = cursor.fetchone()
            if result:   # 书籍信息已存在
                self.textEdit.append("书籍信息已存在")
                self.textEdit.append(f"书名: {bookname}, 书号: {bookid}")
            else:   # 书籍信息不存在，可以插入
                self.insert_sql(db, bookname, bookid)
        except pymysql.Error as e:
            print(f"数据库查询失败: {e}")
            self.textEdit.append("数据库查询失败")
            self.textEdit.append(f"书名: {bookname}, 书号: {bookid}")

    def insert_sql(self, db, bookname, bookid):

        cursor = db.cursor()
        sql = "INSERT INTO library (bookname, bookid) VALUES (%s, %s)"
        try:
            cursor.execute(sql, (bookname, bookid))
            db.commit()
            print("数据插入成功")
            self.textEdit.append("数据插入成功")
            self.textEdit.append(f"书名: {bookname}, 书号: {bookid}")
        finally:
            db.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = recognize_figure()
    MainWindow.show()
    sys.exit(app.exec_())
