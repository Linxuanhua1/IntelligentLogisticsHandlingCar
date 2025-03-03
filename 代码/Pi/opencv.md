##### 1、导入库

```
import cv2
# 导入库
```

##### 2、读取图片

```
image = cv2.imread("path", method)
"""
读取图片信息，会返回一个图片对象，可以指定读取方法，默认为cv2.IMREAD_COLOR
常用的读取方法
cv2.IMREAD_UNCHANGED 读取图像并包括图像的 Alpha 通道（如果存在的话）
cv2.IMREAD_GRAYSCALE 以灰度模式读取图像，返回一个单通道的灰度图像。
cv2.IMREAD_ANYCOLOR 以任何可能的颜色格式读取图像
cv2.IMREAD_ANYDEPTH 以图像的实际深度读取图像
cv2.IMREAD_REDUCED_COLOR_2 以降低一半的分辨率读取图像，并以彩色模式返回图像
cv2.IMREAD_REDUCED_COLOR_4 以降低四分之一的分辨率读取图像，并以彩色模式返回图像
cv2.IMREAD_REDUCED_COLOR_8 以降低八分之一的分辨率读取图像，并以彩色模式返回图像
cv2.IMREAD_REDUCED_GRAYSCALE_2 以降低一半的分辨率读取图像，并以灰度模式返回图像
cv2.IMREAD_REDUCED_GRAYSCALE_4 以降低四分之一的分辨率读取图像，并以灰度模式返回图像
cv2.IMREAD_REDUCED_GRAYSCALE_8 以降低八分之一的分辨率读取图像，并以灰度模式返回图像
"""
image.shape  
# 返回图片的三维信息，长宽和色彩通道
# 数据类型如右，[宽度：长度：色彩通道数量]
# opencv的RGB三原色顺序是反过来的，默认0是B，1是G，2是R
```

##### 3、显示图片

```
cv2.imshow("WindowName", image_var)  
# 第一个变量为窗口名，第二个为图片对象，函数作用是显示图片
```

##### 4、延时等待

```
cv2.waitKey()  
# 等待键入字符，有字符输入就停止显示，可以传入delay参数，到达时间没有输入就执行后续代码
```

##### 5、色彩空间转换

```
cv2.cvtColor(image, cvt_way)  
# 用来转换颜色空间的函数，第一个变量是图片对象，第二个变量是转换方法
# 常用的转换方法有
# COLOR_BGR2GRAY:将BGR格式的图像转换为灰度图
# COLOR_BGR2HSV:将BGR格式的图像转换为HSV格式
# COLOR_BGR2LAB:将BGR格式的图像转换为LAB格式
# COLOR_BGR2Luv:将BGR格式的图像转换为Luv格式
# COLOR_BGR2RGB:将BGR格式的图像转换为RGB格式
# COLOR_BGR2XYZ:将BGR格式的图像转换为XYZ格式
# COLOR_BGR2YUV:将BGR格式的图像转换为YUV格式
# COLOR_BGR2YCrCb:将BGR格式的图像转换为YCrCb格式
# COLOR_HSV2BGR:将HSV格式的图像转换为BGR格式
# COLOR_HSV2RGB:将HSV格式的图像转换为RGB格式
# COLOR_LAB2BGR:将LAB格式的图像转换为BGR格式
# COLOR_LAB2Luv:将LAB格式的图像转换为Luv格式
# COLOR_LAB2RGB:将LAB格式的图像转换为RGB格式
# COLOR_Luv2BGR:将Luv格式的图像转换为BGR格式
# COLOR_Luv2RGB:将Luv格式的图像转换为RGB格式
# COLOR_RGB2BGR:将RGB格式的图像转换为BGR格式
# COLOR_RGB2HSV:将RGB格式的图像转换为HSV格式
# COLOR_RGB2LAB:将RGB格式的图像转换为LAB格式
# COLOR_RGB2Luv:将RGB格式的图像转换为Luv格式
# COLOR_RGB2YUV:将RGB格式的图像转换为YUV格式
# COLOR_RGB2YCrCb:将RGB格式的图像转换为YCrCb格式
# COLOR_XYZ2BGR:将XYZ格式的图像转换为BGR格式
# COLOR_XYZ2RGB:将XYZ格式的图像转换为RGB格式
# COLOR_YUV2BGR:将YUV格式的图像转换为BGR格式
# COLOR_YUV2RGB:将YUV格式的图像转换为RGB格式
# COLOR_YCrCb2BGR:将YCrCb格式的图像转换为BGR格式
# COLOR_YCrCb2RGB:将YCrCb格式的图像转换为RGB格式
# COLOR_YCrCb420p2BGR:将YCrCb420p格式的图像转换为BGR格式
# COLOR_YCrCb420p2RGB:将YCrCb420p格式的图像转换为RGB
```

##### 6、裁剪图片

```
image = cv2.imread('1.jpg')
crop = image[start:end, start:end] 
# cv2裁剪图片，注意！图片长宽是先宽后长！！
```

##### 7、画几何图形和显示文本

```
# opencv存储的图片对象是一个numpy数组
image = np.zeros([300, 300, 3], dtype=np.uint8)
```

```
# 画线
cv2.line(image, (start_x,start_y), (end_x, end_y), (blue, green, red), thickness)
# 第一个为图片对象，第二个为起点坐标，第三个为终点坐标，第四个为颜色，第五个为线条粗细

# 画矩形框
cv2.rectangle(image, (start_x,start_y), (end_x, end_y), (blue, green, red), thickness)
# 第一个为图片对象，第二个为矩形框起点坐标，第三个为矩形框对角坐标，第四个为颜色，第五个为线条粗细

# 画圆
cv2.circle(image, (centre_x,centre_y), radius, (blue, green, red), thickness)
# 第一个为图片对象，第二个为圆心坐标（必须为整数），第三个为半径，第四个为颜色，第五个为线条粗细

# 显示字符
cv2.putText(image, "text", (start_x, start_y), fontscale, (blue, green, red), thickness)
# 第一个为图片对象，第二个为文本信息，第三个为起点坐标，第四个为缩放比例，第五颜色，第六个为粗细
```

##### 8、去除图片噪点

```
# 去除噪点的算法
cv2.GaussianBlur(image, (sizex, sizey), SigmaX)
# 高斯滤波器，第一个是图片对象，第二个是高斯核大小，第三个参数是x方向的标准差

median = cv2.medianBlur(image, ksize)
# 中值滤波器，第一个是图片对象，第二个是核大小
```

##### 9、获取图片轮廓的特征点

```
# 获取图片特征点的函数
corners = cv2.goodFeaturesToTrack(gray, 500, 0.1, 10)
# 第一个是灰度图，第二个是最大特征点数量，第二个是精度，第三个是特征点之间最小间距

# 示例
image = cv2.imread("opencv_logo.jpg")
# 获取特征点需要先转换成灰度图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# 检测角点的函数
corners = cv2.goodFeaturesToTrack(gray, 500, 0.1, 10)
for corner in corners:
    x, y = corner.ravel()  # 将二维数组转换成一维数组
    cv2.circle(image, (int(x), int(y)), 3, (255, 0, 255), -1)  # 宽度为-1就是画点

cv2.imshow("corners", image)
cv2.waitKey()
```

##### 10、查找图片中类似的特征

```
# 匹配特征
cv2.matchTemplate(gray, templeate, match_way)

"""
第一个是灰度图，第二个是样板，第三个是匹配方法
常见的匹配算法
cv2.TM_SQDIFF 平方差匹配
cv2.TM_SQDIFF_NORMED 归一化平方差匹配
cv2.TM_CCORR 相关匹配
cv2.TM_CCORR_NORMED 归一化相关匹配
cv2.TM_CCOEFF 相关系数匹配
cv2.TM_CCOEFF_NORMED 归一化相关系数匹配
"""

# 示例
mage = cv2.imread("poker.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

template = gray[75:105, 235:265]

match = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)  
# 返回的是每一个点的匹配相似度，是二维数组
locations = np.where(match >= 0.9)
# 返回match数组里>=0.9的点
 
w, h = template.shape[0:2]
for p in zip(*locations[::-1]):
    x1, y1 = p[0], p[1]
    x2, y2 = x1 + w, y1 + h
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

cv2.imshow("image", image)
cv2.waitKey()
```

##### 11、检测边缘

```
# 使用梯度算法检测边缘
cv2.Laplacian(gray, cv2.cv_64F)
"""
拉普拉斯算法，第一个是灰度图，第二个是输出图像的深度
CV_8U : 8-bit unsigned integers (0..255)
CV_16U: 16-bit unsigned integers (0..65535)
CV_16S: 16-bit signed integers (-32768..32767)
CV_32F: 32-bit floating point numbers
CV_64F: 64-bit floating point numbers
输出图像的深度决定了计算结果的精度和范围。由于拉普拉斯算子是一个二阶导数操作，计算结果可能包含负值，并且在许多情况下会超过输入图像的范围。为了确保计算结果的精度和避免溢出，通常会选择 CV_64F（64位浮点数）作为输出图像的深度。
"""

cv2.Canny(gray, threshold1, threshold2)
# Canny算法，第一个是灰度图，第二个是阈值1，第三个是阈值2
# 当两侧阈值超出设定值，则设定该点为边缘
```

##### 12、阈值算法

```
# 阈值算法
ret, binary = cv2.threshold(gray, thresh, maxval, method)
"""
第一个是灰度图，第二个是阈值，第三个是最大值，第三个是阈值处理类型
常用的阈值处理类型
cv2.THRESH_BINARY 如果像素值大于阈值，则设置为最大值，否则设置为0。
cv2.THRESH_BINARY_INV 如果像素值大于阈值，则设置为0，否则设置为最大值。
cv2.THRESH_TRUNC 如果像素值大于阈值，则设置为阈值，否则保持不变。
cv2.THRESH_TOZERO 如果像素值大于阈值，则保持不变，否则设置为0。
cv2.THRESH_TOZERO_INV 如果像素值大于阈值，则设置为0，否则保持不变。
cv2.THRESH_OTSU 使用 Otsu 的方法自动计算阈值，然后应用 cv2.THRESH_BINARY 类型。
cv2.THRESH_TRIANGLE 使用三角法自动计算阈值，然后应用 cv2.THRESH_BINARY 类型
"""

# 自适应阈值算法
binary_adaptive = cv2.adaptiveThreshold(gray, maxValue, adaptiveMethod, thresholdType, blockSize, C)
"""
第一个是灰度图，第二个是阈值处理后输出的最大值，第三个是自适应计算方法，第四个是阈值类型，第五个是计算阈值时的邻域块大小，六个是从计算出的均值或加权均值中减去的常数，用于微调阈值
常用自适应阈值计算方法
cv2.ADAPTIVE_THRESH_MEAN_C 阈值是邻域块内所有像素值的平均值减去常数 C
cv2.ADAPTIVE_THRESH_GAUSSIAN_C 阈值是邻域块内像素值的加权和（权重为一个高斯窗口）减去常数 C
示例代码
binary_adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
"""

# 大金算法
ret1, binary_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
```

##### 13、形态学算法

```
# 图像的形态学算法
# 需要先定义一个核且传入的图像必须是二值图，所以需要先对图像进行阈值算法
kernel = np.ones((5, 5), np.uint8)
# 腐蚀
erosion = cv2.erode(binary, kernel)

# 膨胀
dilation = cv2.dilate(binary, kernel)
```

##### 14、调用摄像头

```
# 调用摄像头

capture = cv2.VideoCapture(index)
# 传入摄像头索引，从0开始

ret, frame = capture.read()
# read会返回两个值，第一个是是否读取成功的bool值，第二个是图片对象

cature.release()
# 释放对象
```

##### 15、圆心检测

```
# 霍夫圆检测
circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1,minDist=300, param1=200, param2=100, minRadius=0, maxRadius=0)
""""
第一个是图片，第二个是检测算法（就这一种）
第三个是霍夫空间（越大精度越高，同时运算速度变慢）
第四个圆心之间的间距
第五个边缘检测时使用Canny算子的高阈值，低阈值是高阈值的一半
第六个是检测阶段圆心的累加器阈值，它越小，可能检测到的假圆越多。
七和八如英文所示，圆的最大最小半径（单位：像素）
"""
```

##### 16、二维码检测

```
# 二维码扫描
qrcode = cv2.QRCodeDetector()  # 初始化二维码识别对象
QR, points, code = qrcode.detectAndDecode(frame)  
# 查找并解码二维码，会返回三个值，第一个是二维码解码的字符串，第二个是二维码的角点，第三个是否查找到二维码
```

##### 17、查找图像轮廓的角点

```
""""
寻找物体的轮廓
cv2.findContours(image, mode, method)函数来找到二值图像中的轮廓。
参数：
参数1：输入的二值图像。通常是经过阈值处理后的图像，例如在颜色过滤之后生成的掩码。
参数2(cv2.RETR_EXTERNAL)：轮廓的检索模式。有几种模式可选，常用的包括：
cv2.RETR_EXTERNAL：只检测最外层的轮廓。
cv2.RETR_LIST：检测所有的轮廓并保存到列表中。
cv2.RETR_CCOMP：检测所有轮廓并将其组织为两层的层次结构。
cv2.RETR_TREE：检测所有轮廓并重构整个轮廓层次结构。
参数3(cv2.CHAIN_APPROX_SIMPLE)：轮廓的近似方法。有两种方法可选，常用的有：
cv2.CHAIN_APPROX_SIMPLE：压缩水平、垂直和对角线方向上的所有轮廓，只保留端点。
cv2.CHAIN_APPROX_NONE：保留所有的轮廓点。
返回值：
contours：包含检测到的轮廓的列表。每个轮廓由一系列点组成。
_（下划线）：层次信息，通常在后续处理中可能会用到。在这里，我们通常用下划线表示我们不关心这个返回值。
""""
contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
```

