"""
用户端人脸登录系统

"""
import qdarkstyle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QMessageBox

from ui.face_UI import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from seetaface.api import *
import pymysql
from sql import host, user, passwd, db2
from user_system import UserMainWindow


class face_MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.new_page_Window = UserMainWindow() # 子界面

        self.setWindowTitle("用户端图书借阅系统")

        self.update_timer = QtCore.QTimer()
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # 打开摄像头

        # self.show_camera()  # 显示摄像头
        self.camera.set(6, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
        self.camera.set(3, 480)
        self.camera.set(4, 640)
        self.update_timer.start(30)  # 设置定时器，每隔30ms刷新一次摄像头
        self.update_timer.timeout.connect(self.show_camera)  # 连接刷新函数

        self.log_in.clicked.connect(self.log_in_system)  # 识别人脸
        self.log_out.clicked.connect(self.log_out_system)  # 登录系统
        self.pushButton.clicked.connect(self.register_system)  # 人脸识别按钮
        #  seetaface初始化
        self.init_mask = FACE_DETECT | FACERECOGNITION | LANDMARKER5
        self.seetaFace = SeetaFace(self.init_mask)  # 初始化
        self.results = None  # 存储查询结果


    def connect_sql(self):
        # 连接数据库
        db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
        cursor = db.cursor()
        return db, cursor

    def new_page(self):
        # 打开子界面
        self.hide() # 隐藏当前界面
        self.new_page_Window.show()
        # 调用select_sql方法
        self.new_page_Window.select_sql(self.results)
        self.new_page_Window.exit.clicked.connect(self.close_page)

    def close_page(self):
        # 关闭子界面
        self.new_page_Window.close()
        self.show() # 显示当前界面
    def select_one_sql(self):
        db, cursor = self.connect_sql()
        sql = "SELECT * FROM name_feature"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            db.close()
            return results
        except:
            print("Error: unable to fetch data")
            cursor.close()
            db.close()

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
            self.camera_label.setPixmap(QtGui.QPixmap.fromImage(q_image))  # 显示图片
            self.camera_label.setScaledContents(True)  # 图片自适应大小
            self.camera_label.setAlignment(Qt.AlignCenter)  # 图片居中
            return

    def request_face(self):
        """
        # 人脸识别
        :param frame: 用户的人脸图片
        :return:
        """
        _, frame = self.camera.read()  # 读取摄像头数据
        detect_result = self.seetaFace.Detect(frame)  # 人脸检测，返回人脸检测信息数组
        Feature = []
        if detect_result.size == 0:  # 当未检测到人脸时
            print("登录失败,请确认人脸是否录入!!!\n若已录入请面向摄像头切勿遮挡人脸!!!")
            QMbox = QMessageBox()
            QMbox.setWindowTitle("提示")
            QMbox.setText("登录失败,请确认人脸是否录入!!!\n若已录入请面向摄像头切勿遮挡人脸!!!")
            QMbox.exec_()
            return  # 函数返回，避免无用的运算时间
        for i in range(detect_result.size):  # 遍历每一个人的人脸数据
            face = detect_result.data[i].pos
            points = self.seetaFace.mark5(frame, face)  # 5点检测模型检测
            feature = self.seetaFace.Extract(frame, points)  # 在一张图片中提取指定人脸关键点区域的人脸的特征值
            feature = self.seetaFace.get_feature_numpy(feature)  # 获取feature的numpy表示数据
            Feature.append(feature)
        results = self.select_one_sql()
        self.results = results
        similar = []
        for i in Feature:
            for j in results:
                if j[1] is not None:
                    feature_sql = np.frombuffer(j[1], dtype=np.float32)
                    similar1 = self.seetaFace.compare_feature_np(feature_sql, i)  # 使用numpy计算，比较人脸特征值相似度
                    similar.append(similar1)
                    # print(similar)
        if float(max(similar)) > 0.65:  # 当相似度大于0.65时
            # 打印出人名和学号
            QMbox = QMessageBox()
            QMbox.setWindowTitle("提示")
            QMbox.setText(f"欢迎{results[(similar.index(max(similar)))][0]}同学登录系统")
            QMbox.exec_()
            print(results[(similar.index(max(similar)))][0], results[(similar.index(max(similar)))][3])
            print("存在")
        else:
            # print(results[(similar.index(max(similar)))][0], results[(similar.index(max(similar)))][3])
            QMbox = QMessageBox()
            QMbox.setWindowTitle("警告")
            QMbox.setText(f"抱歉，{results[(similar.index(max(similar)))][0]}同学未登录系统")
            QMbox.exec_()
            print("不存在")
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
        if detect_result.size == 0:  # 当未检测到人脸时
            print("登录失败,请确认人脸是否录入!!!\n若已录入请面向摄像头切勿遮挡人脸!!!")
            QMbox = QMessageBox()
            QMbox.setWindowTitle("提示")
            QMbox.setText("登录失败,请确认人脸是否录入!!!\n若已录入请面向摄像头切勿遮挡人脸!!!")
            QMbox.exec_()
            return # 函数返回，避免无用的运算时间
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
            cursor.execute(sql, ('吴佳航', data, '1', '2303080206', '男', '18115211948'))
            db.commit()
            print("数据插入成功")
            QMbox = QMessageBox()
            QMbox.setWindowTitle("提示")
            QMbox.setText("注册成功")
            QMbox.exec_()
        except pymysql.Error as e:
            print(f"数据库插入失败: {e}")
            QMbox = QMessageBox()
            QMbox.setWindowTitle("提示")
            QMbox.setText("数据库插入失败: {}").format(e)
            QMbox.exec_()
        finally:
            cursor.close()
            db.close()
    def log_in_system(self):
        # 登录系统
        self.request_face()  # 人脸识别
        self.new_page()
    def log_out_system(self):
        self.camera_label.clear()  # 清空摄像头显示
        # 关闭摄像头
        self.camera.release()
        # 关闭窗口
        self.close()


if __name__ == "__main__":
    import sys

    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QtWidgets.QApplication(sys.argv)
    # 使用 qdarkstyle

    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    MainWindow = face_MainWindow()
    MainWindow.show()



    sys.exit(app.exec_())
