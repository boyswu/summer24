import queue
import threading
import cv2
import numpy as np
from PyQt5.QtWidgets import QFileDialog
import os
from UI import Ui_MainWindow
from PyQt5 import QtWidgets, QtGui
import pymysql


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
            return
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
        # 形态学操作，填充孔洞 膨胀
        kernel = np.ones((3, 3), np.uint8)
        dilation = cv2.dilate(erosion, kernel, iterations=1)
        # cv2.imshow('膨胀', dilation)
        # cv2.waitKey(0)

        # 小轮廓去除
        contours, _ = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # draw_img1 = cv2.cvtColor(erosion, cv2.COLOR_GRAY2RGB)
        # # # 绘制轮廓
        # res = cv2.drawContours(draw_img1, contours, -1, (0, 0, 255), 2)
        # cv2.imshow("res3", res)
        # cv2.waitKey(0)
        fill = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:
                fill.append(contour)
        thresh = cv2.fillPoly(erosion, fill, (255, 255, 255))

        # 再次轮廓检测
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        # 遍历轮廓并绘制矩形框
        for contour in contours:
            # 计算轮廓的面积e
            area = cv2.contourArea(contour)
            # if int(area) < 1500 and int(area) > 500:
            if int(area) < 3000:
                # 计算轮廓的边界框
                x, y, w, h = cv2.boundingRect(contour)

                # 绘制矩形框
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return thresh

    def mode_match(self):
        # 加载数字模板
        template_files = ['0.jpg', '1.jpg', '2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.jpg', '7.jpg', '8.jpg', '9.jpg',
                          '10.jpg', '11.jpg'
                          ]  # 根据实际情况填写模板文件名
        # 创建一部字典，将模板文件名映射到对应的值
        template_values = {
            '0.jpg': 1,
            '1.jpg': 7,
            '2.jpg': 1,
            '3.jpg': 2,
            '4.jpg': '.',
            '5.jpg': 4,
            '6.jpg': 5,
            '7.jpg': '/',
            '8.jpg': 'B',
            '9.jpg': 7,
            '10.jpg': 5,
            '11.jpg': 7
        }
        # 加载数字模板并赋值
        templates = {}
        for file in template_files:
            value = template_values[file]
            templates[value] = cv2.imread('./numbers/' + file, 0)
            # 这里可以添加一些模板处理操作，如灰度化、二值化、滤波等
            # 二值化
            templates[value] = cv2.threshold(templates[value], 127, 255, cv2.THRESH_BINARY)[1]
            # #膨胀
            # templates[value] = cv2.dilate(templates[value], np.ones((3, 3), np.uint8), iterations=1)
            # 腐蚀
            templates[value] = cv2.erode(templates[value], np.ones((3, 3), np.uint8), iterations=1)
            # 高斯模糊
            templates[value] = cv2.GaussianBlur(templates[value], (5, 5), 0)
            # cv2.imshow(str(value), templates[value])
            # cv2.waitKey(0)
            templates[value] = cv2.resize(templates[value], (200, 300))
            # cv2.imshow(str(value), templates[value])
            # cv2.waitKey(0)
        # 读取目标图像并进行预处理
        # img = self.recognize()

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
            # 保存起来后面再次imread转成灰度图进行模板匹配
            cv2.imwrite('jietu.jpg', img)
            # 切割图片
            best_match = -1
            best_score = float('-inf')  # 改为负无穷，因为cv2.TM_CCOEFF_NORMED的score越高越好
            # 遍历模板
            for value, template in templates.items():  # 遍历模板，value为模板值，template为模板图片
                # 匹配模板
                img = cv2.imread('jietu.jpg', 0)
                img = cv2.resize(img, (200, 300))
                # cv2.imshow("SHUOimg", img)
                # cv2.waitKey(0)
                # 匹配模板

                # cv2.imshow("res", res)
                res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
                _, score, _, _ = cv2.minMaxLoc(res)
                if score > best_score:  # 改为大于号，因为cv2.TM_CCOEFF_NORMED的score越高越好
                    # print("最佳匹配：", best_score)
                    # print("当前匹配：", score)
                    # print("当前模板值：", value)
                    # print("当前模板图片：", template)
                    best_score = score
                    # print("最佳匹配：", best_score)
                    # 选择最佳匹配的模板值作为识别结果
                    best_match = value
                if best_match == -1:  # 没有匹配到任何模板
                    # unknown = "没有匹配到任何模板"
                    # self.textEdit.append(unknown)
                    # print(unknown)
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

        db = pymysql.connect(host='8.147.233.239', user='root', passwd='team2111', db='wjh',
                             charset='utf8')
        cursor = db.cursor()
        # 查询数据表里的数据
        sql = "SELECT bookname FROM library WHERE bookid = %s"
        try:
            cursor.execute(sql, (result_str,))
            db.commit()
            # 获取查询结果
            results = cursor.fetchall()
            # 输出查询结果
            for row in results:
                print(row[0])
                self.textEdit.append(row[0])
                db.close()
        except:
            print("Error: unable to fetch data")
        db.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = recognize_figure()
    MainWindow.show()
    sys.exit(app.exec_())
