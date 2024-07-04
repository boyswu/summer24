import queue
import threading
import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog
import os
from UI import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui
import pymysql
from sql import host, user, passwd, db2


class recognize_figure(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(recognize_figure, self).__init__(parent)

        self.setupUi(self)

        self.cwd = os.getcwd()  # 获取当前程序文件位置
        self.before_photo.setScaledContents(True)  # 图片自适应大小
        self.after_photo.setScaledContents(True)  # 图片自适应大小
        self.result_queue = queue.Queue()  # 队列

        self.goal_file.clicked.connect(self.open_file)
        self.start.clicked.connect(self.mode_match)

    def open_file(self):
        path = QFileDialog.getOpenFileName(self,
                                           "选取文件",
                                           self.cwd,  # 起始路径
                                           "Image Files (*.jpg *.png *.jpeg *.bmp)")  # 设置文件扩展名过滤,用双分号间隔
        if path == "":
            print("取消选择")
            self.textEdit.append("取消选择")
        else:
            print("\n你选择的文件夹为:", path)
            self.path = path[0]
            # 读取图像
            image = cv2.imread(self.path)

            img = self.label_img(image)
            # 固定 QLabel 的大小
            self.before_photo.setFixedSize(500, 300)  # 设置你希望的固定大小
            self.before_photo.setPixmap(QtGui.QPixmap.fromImage(img))

            return path

    def recognize_wrapper(self):
        result = self.recognize()
        self.result_queue.put(result)

    def label_img(self, img):
        if img is None:
            return QtGui.QImage()

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
        img = QtGui.QImage(img.data, img.shape[1], img.shape[0],
                           int(img.shape[1]) * 3,
                           QtGui.QImage.Format_RGB888)  # 把读取到的视频数据变成QImage形式
        return img

    def reduce_img(self, image, img):  # image原图，img为框出矩阵后的图片
        cnts = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # 获取图片中的轮廓
        c = max(cnts, key=cv2.contourArea)  # 在边界中找出面积最大的区域
        rect = cv2.minAreaRect(c)  # 绘制出该区域的最小外接矩形
        box = cv2.boxPoints(rect)  # 记录该矩形四个点的位置坐标
        box = np.intp(box)  # 将坐标转化为整数

        x, y, w, h = cv2.boundingRect(box)  # 获取最小外接轴对齐矩形的坐标

        img = image[y:y + h, x:x + w]  # 获取roi区域
        return img

    def recognize(self):
        # 读取图像
        image = cv2.imread(self.path)
        # 转换到HSV颜色空间
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # 定义绿色的HSV范围
        lower_green = np.array([35, 43, 46])
        upper_green = np.array([77, 255, 255])

        # 提取绿色区域
        mask = cv2.inRange(hsv, lower_green, upper_green)
        img = self.reduce_img(image, mask)

        cv2.imwrite('result.jpg', img)  # 保存图片
        # 仿射变换
        rows, cols, ch = img.shape
        pts1 = np.float32([[0, 0], [0, rows], [cols, rows], [cols, 0]])
        pts2 = np.float32([[0, 0], [0, rows], [cols, rows], [cols, 0]])
        M = cv2.getPerspectiveTransform(pts1, pts2)
        dst = cv2.warpPerspective(img, M, (cols, rows))
        # cv2.imshow("dst", dst)
        # 转换为灰度图像
        gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('gray', gray)
        # cv2.waitKey(0)
        # 二值化处理
        ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # cv2.imshow('二值化', binary)
        # cv2.waitKey(0)
        # 反色处理
        binary = 255 - binary
        # cv2.imshow('反色', binary)
        # cv2.waitKey(0)
        # 形态学操作，去除噪声 腐蚀
        kernel = np.ones((3, 3), np.uint8)
        erosion = cv2.erode(binary, kernel, iterations=1)
        # cv2.imshow('腐蚀', erosion)
        # cv2.waitKey(0)
        # # 形态学操作，填充孔洞 膨胀
        # kernel = np.ones((3, 3), np.uint8)
        # dilation = cv2.dilate(erosion, kernel, iterations=1)
        # # cv2.imshow('膨胀', dilation)
        # # cv2.waitKey(0)

        # 小轮廓去除
        contours, _ = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        fill = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:
                fill.append(contour)
        thresh = cv2.fillPoly(erosion, fill, (255, 255, 255))

        return thresh

    def mode_match(self):
        # 定义模板文件夹
        folders = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            'dian': '.',
            'xiegang': '/',
                'B': 'B',
            'Y': 'Y'
        }
        # 创建一部字典来存储模板图片
        templates = {}
        # 遍历每个文件夹
        for folder, value in folders.items(): # 遍历字典,folder为键，value为值
            folder_path = os.path.join('./moban', folder)
            if os.path.isdir(folder_path):
                # 获取文件夹中的所有图片文件
                files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]
                # 加载每个图片文件并存储到字典中
                for file in files:
                    file_path = os.path.join(folder_path, file)
                    template_img = cv2.imread(file_path, 0)
                    if template_img is not None:
                        if value not in templates:
                            templates[value] = []
                        templates[value].append(template_img)
        # 遍历每个模板，进行预处理
        for value, template_list in templates.items():
            # 遍历模板列表，对每个模板进行预处理
            for i in range(len(template_list)):
                template = template_list[i]
                # 二值化
                template = cv2.threshold(template, 127, 255, cv2.THRESH_BINARY)[1]
                # #膨胀
                # template = cv2.dilate(template, np.ones((3, 3), np.uint8), iterations=1)
                # 腐蚀
                template = cv2.erode(template, np.ones((3, 3), np.uint8), iterations=1)
                # 高斯模糊
                template = cv2.GaussianBlur(template, (5, 5), 0)
                # 缩放
                template = cv2.resize(template, (200, 300))
                template_list[i] = template
                # cv2.imshow("template", template)
                # cv2.waitKey(0)

        img_thread = threading.Thread(target=self.recognize_wrapper, args=())
        img_thread.setDaemon(True)  # 设置为守护线程，主线程结束后自动结束
        img_thread.start()  # 启动线程
        img_thread.join()  # 等待线程完成
        img = self.result_queue.get()
        # cv2.imshow("img", img)
        # cv2.waitKey(0)
        # 对图片进行腐蚀 ，缩小图片
        kernel = np.ones((50, 50), np.uint8)
        image = cv2.erode(img, kernel, iterations=1)
        # cv2.imshow("image", image)
        # cv2.waitKey(0)
        roi = self.reduce_img(img, image)
        contours, _ = cv2.findContours(roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # 遍历轮廓并进行模板匹配
        # 首先将轮廓按照 x 坐标排序 从左到右
        sorted_contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
        result = []
        for contour in sorted_contours:
            # 计算轮廓的面积
            area = cv2.contourArea(contour)
            # print("轮廓面积：", area)
            # 计算轮廓的边界框
            x, y, w, h = cv2.boundingRect(contour)
            if 0 < area < 100 or 150 < area < 600 or area > 50000:  # 过滤掉过小的轮廓
                continue
            # 绘制矩形框
            cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

            img = roi[y:y + h, x:x + w]
            # cv2.imshow("img", img)
            # cv2.waitKey(0)
            # 保存起来后面再次imread转成灰度图进行模板匹配
            cv2.imwrite('jietu.jpg', img)
            # 切割图片
            best_match = -1
            best_score = float('-inf')  # 改为负无穷，因为cv2.TM_CCOEFF_NORMED的score越高越好
            img = cv2.imread('jietu.jpg', 0)
            img = cv2.resize(img, (200, 300))
            # 遍历模板
            for value, template_list in templates.items():
                for template in template_list:

                    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                    _, score, _, _ = cv2.minMaxLoc(res)
                    if score > best_score:  # 改为大于号，因为cv2.TM_CCOEFF_NORMED的score越高越好
                        best_score = score
                        best_match = value
                    if best_match == -1:  # 没有匹配到任何模板
                        print("没有匹配到任何模板")
                        continue
            # 在循环结束后输出最佳匹配的模板值
            print("最终最佳匹配的模板值：", best_match)
            # 将for循环best_match的值拼接成字符串，输出到textEdit
            img = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)  # 视频色彩转换回RGB，这样才是现实的颜色
            roi = cv2.putText(img, str(best_match), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
            img = self.label_img(roi)
            self.after_photo.setFixedSize(500, 300)  # 设置你希望的固定大小
            self.after_photo.setPixmap(QtGui.QPixmap.fromImage(img))
            # 将best_match添加进result列表
            result.append(best_match)
        # 将result列表里的元素合并成字符串，输出到textEdit
        result_str = ''.join(map(str, result))
        self.textEdit.setText(result_str)
        print("最终识别结果：", result_str)
        # 连接数据库
        self.connect_sql(result_str)

    def connect_sql(self, result_str):

        db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
        cursor = db.cursor()
        # 查询数据表里的数据
        sql = "SELECT bookname FROM library WHERE bookid = %s"
        try:
            cursor.execute(sql, result_str)
            # db.commit()
            # 获取查询结果
            results = cursor.fetchall()
            # 输出查询结果
            for row in results:
                print('查询结果：', row[0])
                self.textEdit.append(f"查询结果：{row[0]}")


        except pymysql.Error as e:
            print("Error: unable to fetch data", e)
            self.textEdit.append("Error: unable to fetch data", e)
        finally:
            db.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = recognize_figure()
    MainWindow.show()
    sys.exit(app.exec_())
