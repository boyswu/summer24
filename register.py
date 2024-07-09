"""
用户端人脸登录系统

"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QMessageBox

from ui.register_UI import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from seetaface.api import *
import pymysql
from sql import host, user, passwd, db2


class register_MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.setWindowTitle("用户端图书借阅系统")

        self.update_timer = QtCore.QTimer()
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 打开摄像头

        # self.show_camera()  # 显示摄像头
        self.camera.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        self.camera.set(3, 480)
        self.camera.set(4, 640)
        self.update_timer.start(30)  # 设置定时器，每隔30ms刷新一次摄像头
        self.update_timer.timeout.connect(self.show_camera)  # 连接刷新函数
        self.log_in.clicked.connect(self.register_system)  # 人脸识别按钮
        #  seetaface初始化
        self.init_mask = FACE_DETECT | FACERECOGNITION | LANDMARKER5
        self.seetaFace = SeetaFace(self.init_mask)  # 初始化
        self.results = None  # 存储查询结果

    def connect_sql(self):
        # 连接数据库
        db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
        cursor = db.cursor()
        return db, cursor

    def show_camera(self):
        """显示摄像头"""
        # 打开摄像头
        ret, img = self.camera.read()  # 读取摄像头数据
        if ret:
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换颜色空间
            frame = cv2.flip(frame, 1)  # 水平翻转
            height, width, bytesPerComponent = frame.shape  # 获取图片尺寸
            bytesPerLine = bytesPerComponent * width  # 计算每行的字节数
            q_image = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)  # 创建QImage
            self.label.setPixmap(QtGui.QPixmap.fromImage(q_image))  # 显示图片
            self.label.setScaledContents(True)  # 图片自适应大小
            self.label.setAlignment(Qt.AlignCenter)  # 图片居中
            return

    def register_system(self):
        """
        # 人脸识别
        :param frame: 用户的人脸图片
        :return:
        """
        _, frame = self.camera.read()  # 读取摄像头数据
        detect_result = self.seetaFace.Detect(frame)  # 人脸检测，返回人脸检测信息数组
        Feature = []
        user_name = self.name_edit.text()
        user_id = self.id_edit.text()

        if detect_result.size == 0:  # 当未检测到人脸时
            print("登录失败,请确认人脸是否录入!!!\n若已录入请面向摄像头切勿遮挡人脸!!!")
            QtWidgets.QMessageBox.warning(self, "警告", "登录失败,请确认人脸是否录入!!!\n若已录入请面向摄像头切勿遮挡人脸!!!")
            return  # 函数返回，避免无用的运算时间
        reply = QtWidgets.QMessageBox.question(self, '提示', f'是否确认注册',
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.No:
            return
        if reply == QtWidgets.QMessageBox.Yes:
            if user_name == '' or user_id == '':
                QtWidgets.QMessageBox.warning(self, "警告", "姓名或学号不能为空！")
                return
            for i in range(detect_result.size):  # 遍历每一个人的人脸数据
                face = detect_result.data[i].pos
                points = self.seetaFace.mark5(frame, face)  # 5点检测模型检测
                feature = self.seetaFace.Extract(frame, points)  # 在一张图片中提取指定人脸关键点区域的人脸的特征值
                feature = self.seetaFace.get_feature_numpy(feature)  # 获取feature的numpy表示数据
                Feature.append(feature)

            db, cursor = self.connect_sql()
            sql = ("INSERT INTO name_feature(name, feature, place, id, sex, phone) "
                   "VALUES (%s, %s, %s, %s, %s, %s)")
            try:
                print("开始插入数据", Feature)
                # 向数据库中插入数据
                data = feature.tostring()
                cursor.execute(sql, (user_name, data, '1', user_id, '男', '18115211948'))
                db.commit()
                print("数据插入成功")
                QtWidgets.QMessageBox.information(self, "提示", f"{user_name}注册成功！")
            except pymysql.Error as e:
                print(f"数据库插入失败: {e}")
                QtWidgets.QMessageBox.warning(self, "警告", "注册失败！")

            finally:
                cursor.close()
                db.close()


if __name__ == "__main__":
    import sys

    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QtWidgets.QApplication(sys.argv)
    # 使用 qdarkstyle
    #
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.setStyleSheet('''QWidget{background-color:rgb(193, 232, 218);}''')
    MainWindow = register_MainWindow()
    MainWindow.show()

    sys.exit(app.exec_())
