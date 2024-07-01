import cv2
import numpy as np

# 读取图片
image = cv2.imread('1.jpg')

# 将图片从BGR转换为HSV颜色空间
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 设置绿色的阈值范围
lower_green = np.array([35, 43, 46])
upper_green = np.array([77, 255, 255])

# 创建一个掩码，只保留绿色区域
mask = cv2.inRange(hsv, lower_green, upper_green)

# 将掩码应用于原始图像，得到只有绿色区域的图像
green_image = cv2.bitwise_and(image, image, mask=mask)

# 显示处理后的图像


cv2.namedWindow('Original Image', 0)
cv2.resizeWindow('Original Image', 600, 500)
cv2.imshow('Original Image', image)

cv2.namedWindow('Green Image', 0)
cv2.resizeWindow('Green Image', 600, 500)
cv2.imshow('Green Image', green_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
