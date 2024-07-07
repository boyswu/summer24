import cv2
import numpy as np

# 读取原始图像和模板图像
img = cv2.imread('image.jpg', cv2.IMREAD_COLOR)
template = cv2.imread('template.jpg', cv2.IMREAD_COLOR)

# 获取模板的宽度和高度
w, h = template.shape[:-1]

# 进行模板匹配
res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

# 设置阈值
threshold = 0.8

# 找到匹配的位置
loc = np.where(res >= threshold)

# 在原始图像上绘制矩形框
for pt in zip(*loc[::-1]):
    cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)

# 显示结果
cv2.imshow('Detected', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
