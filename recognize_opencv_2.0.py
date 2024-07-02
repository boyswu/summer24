import cv2
import numpy as np

# 读取图像
image = cv2.imread('1.jpg')

# 转换到HSV颜色空间
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定义绿色的HSV范围
lower_green = np.array([35, 43, 46])
upper_green = np.array([77, 255, 255])

# 提取绿色区域
mask = cv2.inRange(hsv, lower_green, upper_green)

cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  # 获取图片中的轮廓
c = max(cnts, key=cv2.contourArea)  # 在边界中找出面积最大的区域
rect = cv2.minAreaRect(c)  # 绘制出该区域的最小外接矩形
box = cv2.boxPoints(rect)  # 记录该矩形四个点的位置坐标
box = np.int0(box)  # 将坐标转化为整数

x, y, w, h = cv2.boundingRect(box)  # 获取最小外接轴对齐矩形的坐标

img = image[y:y + h, x:x + w]  # 获取roi区域

# 显示结果
cv2.namedWindow("Result", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Result", 500, 500)
cv2.imshow("Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
# 对img进行处理
cv2.imwrite('result.jpg', img)  # 保存图片
# 仿射变换
rows, cols, ch = img.shape
pts1 = np.float32([[0, 0], [0, rows], [cols, rows], [cols, 0]])
pts2 = np.float32([[0, 0], [0, rows], [cols, rows], [cols, 0]])
M = cv2.getPerspectiveTransform(pts1, pts2)
dst = cv2.warpPerspective(img, M, (cols, rows))
cv2.imshow("dst", dst)

# 转换为灰度图像
gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
cv2.imshow('gray', gray)
cv2.waitKey(0)
# 二值化处理
ret, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
cv2.imshow('二值化', binary)
cv2.waitKey(0)
#反色处理
binary = 255 - binary
cv2.imshow('反色', binary)
cv2.waitKey(0)
# 形态学操作，去除噪声 腐蚀
kernel = np.ones((3, 3), np.uint8)
erosion = cv2.erode(binary, kernel, iterations=1)
cv2.imshow('腐蚀', erosion)
cv2.waitKey(0)
# 形态学操作，填充孔洞 膨胀
kernel = np.ones((3, 3), np.uint8)
dilation = cv2.dilate(erosion, kernel, iterations=1)
cv2.imshow('膨胀', dilation)
cv2.waitKey(0)

# 小轮廓去除
contours, _ = cv2.findContours(erosion, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
draw_img1 = cv2.cvtColor(erosion, cv2.COLOR_GRAY2RGB)
# # 绘制轮廓
res = cv2.drawContours(draw_img1, contours, -1, (0, 0, 255), 2)
cv2.imshow("res3", res)
cv2.waitKey(0)
fill = []
for contour in contours:
    area = cv2.contourArea((contour))
    if area < 100:
        fill.append(contour)
thresh = cv2.fillPoly(erosion, fill, (255, 255, 255))

cv2.imshow("thresh0", thresh)
cv2.waitKey(0)
# 再次轮廓检测
contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
# 遍历轮廓并绘制矩形框
for contour in contours:
    # 计算轮廓的面积e
    area = cv2.contourArea(contour)
    # if int(area) < 1500 and int(area) > 500:
    if int(area) < 3000 :
    # 计算轮廓的边界框
        x, y, w, h = cv2.boundingRect(contour)

        # 绘制矩形框
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# 显示结果
cv2.imshow('Result', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
# 保存图片
cv2.imwrite('result2.jpg', img)
