# opencv识别出图书的背脊的绿色区域

## 为什么使用hsv图像

首先RGB只是用于形成我们想要的颜色，比如说，我们想要黄色，可以通过三原色形成黄色，不管是明黄还是淡黄，只需要用不同比例进行混合就能得到我们想要的颜色，但是在我们进行编程的过程中不能直接用这个比例 ，需要辅助工具，也就是HSV，所以需要将RGB转化成HSV。HSV用更加直观的数据描述我们需要的颜色，H代表色彩，S代表深浅，V代表明暗。HSV在进行色彩分割时作用比较大。通过阈值的划分，颜色能够被区分出来。

## 使用的函数

### 1. cv2.inRange 函数

**写法**:

```python
mask = cv2.inRange(hsv, lower_green, upper_green)
```

***参数解释***：

- `hsv`：输入的 HSV 颜色空间的图像。
- lower_green指的是图像中低于这个lower_red的值，图像值变为0
- upper_green指的是图像中高于这个upper_red的值，图像值变为0
- 而在lower_red～upper_red之间的值变成255

**作用**

可以在图像中查找位于指定范围内的像素，该函数返回一个二值图像（只有黑白两种颜色）。

利用cv2.inRange函数设阈值提取特定的颜色区域，去除背景部分。

###2. opencv按位与运算**cv2.bitwise_and 函数**

***什么是按位与操作***

按位与操作是指对两幅图像的像素进行逐位比较，当且仅当两幅图像的对应像素值都为1时，结果图像的对应像素值才为1；否则为0。这种操作常用于图像融合、[掩码](https://so.csdn.net/so/search?q=%E6%8E%A9%E7%A0%81&spm=1001.2101.3001.7020)操作等场景。

**写法**: 

```
green_image = cv2.bitwise_and(src1, src2, dst=None, mask=None)
```

**参数解释**：

- src1：第一幅输入图像 
- src2：第二幅输入图像
- dst：可选参数，输出图像，与输入图像具有相同的尺寸和数据类型
- mask：可选参数，掩码图像，用于指定哪些像素进行按位与操作

**作用**

可以从原始图像中提取出特定的颜色区域。

# 提取出图片绿色区域。

```python
# 提取绿色区域
mask = cv2.inRange(hsv, lower_green, upper_green)
cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]#获取图片中的轮廓
c = max(cnts, key=cv2.contourArea) #在边界中找出面积最大的区域
rect = cv2.minAreaRect(c)    # 绘制出该区域的最小外接矩形
box = cv2.boxPoints(rect)   # 记录该矩形四个点的位置坐标
box = np.int0(box)   #将坐标转化为整数

x, y, w, h = cv2.boundingRect(box) #  获取最小外接轴对齐矩形的坐标

img = image[y:y + h, x:x + w]  #获取roi区域
```

![想截图_2024070217325](C:\Users\boys\Desktop\24年暑假学习\4.7号\assets\联想截图_20240702173253.png)

# 进行仿射变换

```python
# 仿射变换
rows, cols, ch = img.shape
pts1 = np.float32([[0, 0], [0, rows], [cols, rows], [cols, 0]])
pts2 = np.float32([[0, 0], [0, rows], [cols, rows], [cols, 0]])
M = cv2.getPerspectiveTransform(pts1, pts2)
dst = cv2.warpPerspective(img, M, (cols, rows))
cv2.imshow("dst", dst)
```

![想截图_2024070221202](C:\Users\boys\Desktop\24年暑假学习\4.7号\assets\联想截图_20240702212028.png)

# 对图片进行灰度处理,二值化处理,反色处理

```python
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
```

二值化:

![想截图_2024070221240](C:\Users\boys\Desktop\24年暑假学习\4.7号\assets\联想截图_20240702212407.png)

反色:

![想截图_20240702212458 - 副](C:\Users\boys\Pictures\联想截图\联想截图_20240702212458 - 副本.png)

#对图片进行形态学操作

```python
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
```

腐蚀:

![71992680169](C:\Users\boys\AppData\Local\Temp\1719926801694.png)

膨胀:

![71992681735](C:\Users\boys\AppData\Local\Temp\1719926817356.png)

# 检查轮廓对小轮廓进行去除

```python
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
```

去除前:

![想截图_2024070221285](C:\Users\boys\Desktop\24年暑假学习\4.7号\assets\联想截图_20240702212852.png)

去除后:

![想截图_2024070221304](C:\Users\boys\Desktop\24年暑假学习\4.7号\assets\联想截图_20240702213042.png)

# 再次进行轮廓检查,框出矩形

```python
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
```

![想截图_2024070221314](C:\Users\boys\Desktop\24年暑假学习\4.7号\assets\联想截图_20240702213142.png)

#github地址

<[boyswu/summer24 (github.com)](https://github.com/boyswu/summer24)>

