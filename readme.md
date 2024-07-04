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

![想截图_2024070217325](C:\Users\boys\Desktop\24年暑假学习\assets\联想截图_20240702173253.png)

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

![想截图_2024070221202](C:\Users\boys\Desktop\24年暑假学习\assets\联想截图_20240702212028.png)

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

![想截图_2024070221240](C:\Users\boys\Desktop\24年暑假学习\assets\联想截图_20240702212407.png)

反色:

![71992681735](C:\Users\boys\Desktop\24年暑假学习\assets\1719926817356.png)

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

![71992680169](C:\Users\boys\Desktop\24年暑假学习\assets\1719926801694.png)膨胀:

![71992681735](C:\Users\boys\Desktop\24年暑假学习\assets\1719926817356.png)

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

![想截图_2024070221285](C:\Users\boys\Desktop\24年暑假学习\assets\联想截图_20240702212852.png)

去除后:

![想截图_2024070221304](C:\Users\boys\Desktop\24年暑假学习\assets\联想截图_20240702213042.png)

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

# 加载数字模板

```python
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
```

# 对先前框出的图片再次操作

```python
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
```

#检测轮廓对处理好的图像的每一个数字框出矩阵然后分割，最后与模板匹配

```python
# cv2.drawContours(roi, contours, -1, (0, 0, 255), 2)
# cv2.imshow("roi", roi)
# cv2.waitKey(0)
# 遍历轮廓并进行模板匹配
for contour in contours:
    # 计算轮廓的边界框
    x, y, w, h = cv2.boundingRect(contour)
    # 绘制矩形框
    img = cv2.rectangle(roi, (x, y), (x + w        contours, _ = cv2.findContours(roi, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
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
        self.connect_sql(result_str), y + h), (0, 255, 0), 2)
    img = self.reduce_img(image, img)
    # 保存起来后面再次imread转成灰度图进行模板匹配
    cv2.imwrite('result.jpg', img)
    # 切割图片
    best_match = -1
    best_score = float('-inf')  # 改为负无穷，因为cv2.TM_CCOEFF_NORMED的score越高越好
    # 遍历模板
    for value, template in templates.items():  # 直接遍历字典的键值对,value 是字典的键，template 是字典的值
        # 匹配模板
        img = cv2.imread('result.jpg', 0)
        # img = cv2.resize(img, (400, 600))
        # cv2.imshow("res", res)
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, _ = cv2.minMaxLoc(res)
        if score > best_score:  # 改为大于号，因为cv2.TM_CCOEFF_NORMED的score越高越好
            best_score = score
            self.best_match = value

            # cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # self.frame = cv2.putText(roi, str(self.best_match), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1,
            #                          (0, 255, 0), 2)
            print("匹配到数字：", self.best_match)

            self.textEdit.append(str(self.best_match))
            img = self.label_img(roi)
            self.after_photo.setFixedSize(500, 300)  # 设置你希望的固定大小
            self.after_photo.setPixmap(QtGui.QPixmap.fromImage(img))

        if best_match == -1:  # 没有匹配到任何模板
            unknown = "没有匹配到任何模板"
            self.textEdit.append(unknown)
            print(unknown)
            continue
```

![想截图_2024070419052](C:\Users\boys\Desktop\24年暑假学习\assets\联想截图_20240704190527.png)

#思路

##对图片进行处理

对原始图像进行绿色区域提取，对绿色区域进行仿射变换，随后，二值化，反色，腐蚀（去噪点）

，进行轮廓检测对小轮廓进行去除。

## 定义模板文件

在不同的文件夹里塞入不同的模板（数字，字母，字符），对每个文件夹进行赋值，创建字典遍历文件夹，将每个图片文件加载并存储到对应的字典里，遍历所有模板进行二值化，膨胀，腐蚀，高斯模糊，缩放每个模板大小（后续模板匹配要求）的操作

## 模板匹配

对处理过的图片，再次进行腐蚀（缩小图像），轮廓检测，计算轮廓面积对不符合的轮廓剔除，然后从左向右绘制矩形框，并且没绘制一次切割一次图片。对切割的图片进行模板匹配操作。



#连接MySQL数据库查询

```python
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
            print('查询结果：', row[0])
            self.textEdit.append(f"查询结果：{row[0]}")


    except pymysql.Error as e:
        print("Error: unable to fetch data", e)
        self.textEdit.append("Error: unable to fetch data", e)
    finally:
        db.close()
```

# 录入书籍

```python
    def book_infromation(self):

        bookname = self.bookname.text()
        bookid = self.bookid.text()
        self.connect_sql(bookname, bookid)

    def connect_sql(self, bookname, bookid):

        try:
            db = pymysql.connect(host=host, user=user, passwd=passwd, db=db2, charset='utf8')
        except pymysql.Error as e:
            print(f"数据库连接失败: {e}")
            return
        sql = "SELECT * FROM library WHERE bookname = %s AND bookid = %s"
        try:
            cursor = db.cursor()
            cursor.execute(sql, (bookname, bookid))
            result = cursor.fetchone()
            if result:   # 书籍信息已存在
                self.textEdit.append("书籍信息已存在")
                self.textEdit.append(f"书名: {bookname}, 书号: {bookid}")
            else:   # 书籍信息不存在，可以插入
                self.insert_sql(db, bookname, bookid)
        except pymysql.Error as e:
            print(f"数据库查询失败: {e}")
            self.textEdit.append("数据库查询失败")
            self.textEdit.append(f"书名: {bookname}, 书号: {bookid}")
        finally:
            db.close()

    def insert_sql(self, db, bookname, bookid):

        cursor = db.cursor()
        sql = "INSERT INTO library (bookname, bookid) VALUES (%s, %s)"
        try:
            cursor.execute(sql, (bookname, bookid))
            db.commit()
            print("数据插入成功")
            self.textEdit.append("数据插入成功")
            self.textEdit.append(f"书名: {bookname}, 书号: {bookid}")
        finally:
            db.close()
```

![想截图_2024070420242](C:\Users\boys\Desktop\24年暑假学习\assets\联想截图_20240704202423.png)

#github地址

<[boyswu/summer24 (github.com)](https://github.com/boyswu/summer24)>

