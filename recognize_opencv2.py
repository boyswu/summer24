import cv2
import numpy as np


def extract_green_histogram(image):
    # 转换为HSV颜色空间
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 设置绿色的阈值范围
    lower_green = np.array([35, 43, 46])
    upper_green = np.array([77, 255, 255])

    # 创建掩码
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # 计算绿色区域的直方图
    hist = cv2.calcHist([hsv], [0], mask, [180], [0, 180])
    cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)

    # 反向投影到原始图像上
    dst = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)

    # 应用掩码
    result = cv2.bitwise_and(image, image, mask=mask)
    return result


# 读取图片
image = cv2.imread('2.jpg')

# 提取绿色部分并显示结果
green_image = extract_green_histogram(image)
cv2.imshow('Green Image', green_image)
cv2.waitKey(0)
cv2.destroyAllWindows()