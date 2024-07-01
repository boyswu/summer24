import cv2
import numpy as np

# 加载图像
image = cv2.imread("2.jpg")

# 转换为 HSV 颜色空间
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定义绿色的范围，并创建一个阈值图像
lower_green = np.array([35, 60, 60])
upper_green = np.array([80, 255, 255])
mask = cv2.inRange(hsv_image, lower_green, upper_green)

# 使用阈值图像对原图进行“开操作”以去除小噪声（可选）
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

# 将阈值图像转换为三通道，以便与原图尺寸匹配进行逻辑与操作
mask_three_channel = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

# 保留绿色部分，其余部分变为黑色
final_image = cv2.bitwise_and(image, mask_three_channel)

cv2.namedWindow('Original Image', 0)
cv2.resizeWindow('Original Image', 600, 500)
cv2.imshow('Original Image', image)

cv2.namedWindow('Green Image', 0)
cv2.resizeWindow('Green Image', 600, 500)
cv2.imshow('Green Image', final_image)

cv2.waitKey(0)
cv2.destroyAllWindows()

# 保存结果
cv2.imwrite("green_label_thresholded.jpg", final_image)