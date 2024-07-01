import cv2
import numpy as np

# 加载图像
image = cv2.imread("2.jpg")

# 转换为 HSV 颜色空间
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定义绿色的范围
lower_green = np.array([35, 60, 60])
upper_green = np.array([80, 255, 255])

# 初始化与原图同样大小的全黑图像
green_image = np.zeros_like(image)

# 遍历每个像素
height, width, _ = image.shape
for y in range(height):
    for x in range(width):
        # 获取当前像素的HSV值
        hsv = hsv_image[y, x]

        # 检查像素是否在绿色范围内
        if np.all(lower_green <= hsv) and np.all(hsv <= upper_green):
            # 如果是绿色，则保留原像素颜色
            green_image[y, x] = image[y, x]
        else:
            # 否则，设置为黑色
            green_image[y, x] = [0, 0, 0]

cv2.namedWindow('Original Image', 0)
cv2.resizeWindow('Original Image', 600, 500)
cv2.imshow('Original Image', image)

cv2.namedWindow('Green Image', 0)
cv2.resizeWindow('Green Image', 600, 500)
cv2.imshow('Green Image', green_image)

cv2.waitKey(0)
cv2.destroyAllWindows()
# 保存结果
cv2.imwrite("green_label_extracted_loop.jpg", green_image)