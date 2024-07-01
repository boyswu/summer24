# opencv识别出图书的背脊号

## 为什么使用hsv图像

首先RGB只是用于形成我们想要的颜色，比如说，我们想要黄色，可以通过三原色形成黄色，不管是明黄还是淡黄，只需要用不同比例进行混合就能得到我们想要的颜色，但是在我们进行编程的过程中不能直接用这个比例 ，需要辅助工具，也就是HSV，所以需要将RGB转化成HSV。HSV用更加直观的数据描述我们需要的颜色，H代表色彩，S代表深浅，V代表明暗。HSV在进行色彩分割时作用比较大。通过阈值的划分，颜色能够被区分出来。

## 使用的函数

### 1. cv2.inRange 函数

**写法**:

 mask = cv2.inRange(hsv, lower_green, upper_green)

***参数解释***：

- `hsv`：输入的 HSV 颜色空间的图像。
- `lower_green`：一个 NumPy 数组，表示绿色范围的下限。
- `upper_green`：一个 NumPy 数组，表示绿色范围的上限。

**作用**

可以在图像中查找位于指定范围内的像素，该函数返回一个二值图像。

###2.**cv2.bitwise_and 函数**

**写法**: 

green_image = cv2.bitwise_and(image, image, mask=mask)

**参数解释**：

- `image`：这是第一个输入图像，也是第二个输入图像。因为 `cv2.bitwise_and` 需要两个输入图像，这里我们使用同一个图像 `image` 作为两个输入。
- `mask=mask`：这是一个掩码图像，用于指定哪些像素需要进行按位与操作。只有掩码图像中对应位置为非零的像素才会被处理。

**作用**

可以从原始图像中提取出特定的颜色区域。

###github地址

<[boyswu/summer24 (github.com)](https://github.com/boyswu/summer24)>

