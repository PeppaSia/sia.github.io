#Preliminaries:
##高斯分布
###定义:
   
   若随机变量 $X\;$服从均值为$u\;$,标准差为$\sigma$的正态分布，即$X\; \sim\; N\left( u,\sigma ^{2} \right)\;$,则其概率密度函数为$\; f\left( x \right)=\frac{1}{\sqrt{2\pi \sigma }}e^{\left( -\frac{^{\left( x-u \right)^{2}}}{2\sigma ^{2}} \right)}\; \; \;$
   
   ![](650px-Normal_Distribution_PDF.svg.png)
   
###性质： $ \alpha \beta$
   
   $ \ E \left( aX+bY \right)=aE \left( X \right)+bE \left( Y \right)\; $
   $Var\left( aX+bY \right)=a^{2}Var\left( X \right)+b^{2}Var\left( Y \right)+2ab\mbox{C}ov\left( X,Y \right)$
   
   
##多元高斯分布
###定义：

类似正态分布，多元正态分布: $X\; \sim\; N\left( u,\ K \right ) \;$  
概率密度函数为 $ p ( x )=(2 \pi)^{\frac{-n}{2}}|K|^{\frac{-1}{2}}exp(\frac{-1}{2}(x- u )^{T}K^{-1}(x-u))$


###高斯分布协方差
https://blog.csdn.net/paulfeng20171114/article/details/80276061

##高斯过程
	
定义[5.wiki]：在概率论和统计学中，高斯过程(Gaussian process)是观测值出现在一个连续域(例如时间或空间)的统计模型。在高斯过程中，连续输入空间中每个点都是与一个正态分布的随机变量相关联。此外，这些随机变量的每个有限集合都有一个多元正态分布。高斯过程的分布是所有那些(无限多个)随机变量的联合分布，正因如此，它是连续域的分布。

感兴趣可以看https://www.youtube.com/watch?v=BS4Wd5rwNwE

或者https://zhuanlan.zhihu.com/p/75589452 了解

简单理解：高斯过程就是一个无限元高斯分布，其均值和方差都是以函数形式体现

延伸：高斯过程回归
https://zhuanlan.zhihu.com/p/76314366



	
##IMU：
###硬件及原理直观理解：
MEMS：https://www.zhihu.com/zvideo/1339249589351215104
	
###IMU噪声模型

IMU测量符合高斯过程->IMU可以用随机过程建模，allan也是用来分析随机过程误差的工具

1. IMU主要误差[1]：

A Summary of Gyro Error Sources

|Error Type|Description|result of Integration|
|--------|---------|---------------|
|Bias|A constant bias $\epsilon$ |A steadily growing angular error $\theta(t)=\epsilon \cdot t $|
|White Noise|White noise with some standard deviation $\sigma$|An angle ranom walk, whose standard deviation $\sigma_\theta(t)=\sigma \cdot \sqrt{\delta t \cdot t}$ grows with the square root of time|
|Temperature Effects|Temperature dependent residual bias|Any residual bias is integrated into the orientation,causing an orientation error which grows linearly with time|
|Calibration|Deterministic errors in scale factors, alignments and gyro linearities|Orientation drift proportional to the rate and duration of motion|
|Bias Instability|Bias fluctuations, usually modelled as a bias random walk|A second-order random walk|


A Summary of Accelerometer Error Sources

|Error Type|Description|result of Integration|
|--------|---------|---------------|
|Bias|A constant bias $\epsilon$ in the accerometer's output signal|A quadratically growing position error $s(t)=\epsilon \cdot \frac{t^2}{2}$|
|White Noise|White noise with some standard deviation $\sigma$|A second-order random walk. The standard deviation of the position error grows as $\sigma_s(t) = \sigma \cdot t^{3/2}\cdot \sqrt {\frac{\delta t}{3}}$|
|Temperature  Effects|Temperature dependent residual bias|Any residual bias causes an error in position which grows quadratically with time|
|Calibration| Deterministic errors in scale factors,alignments and accelerometer linearities|Position drift proportional to the squared rate and duration of acceleration|
|Bias Instability| Bias fluctuations, usually modelled as a bias random walk|A third-order random walk in position|



其他误差：
1. 量化误差
2. nonlinearity
3. repeatbility
4. in run repeatbility
5. linear acceleration effect

1. 误差总结：

	1. Calibration 和 Bias 可以通过参考[2]标定(https://github.com/shenshikexmu/IMUCalibration-Gesture **未验证**)
	2. Bias Instability 和White Noise通过allan方差标定(kalibr\_allan https://github.com/rpng/kalibr\_allan)
	3. 还有很多其他的评价误差的指标，有些会在datasheet指出，Repeatability1、In Run Bas Stability、Linear Acceleration Effect、Sensor Resonant Frequency（谐振频率，频率越高越好，不容易被尖锐声波如汽笛干扰） 可以用来帮助确定Bias等指标是否会有很大的偏差，会不会产生很大的影响(但是也只能通过经验判断或者后期做实验帮助判断)
	4. ADI MEMS提供了一些误差讲解 https://www.eet-china.com/RC/ADI_MEMSVideo/index.html#section02 
	5. 一些噪声带来的影响[7]


2. IMU内参标定(kalibr_allan)：
	1. 标定过程
		1. allan 方差[1][3]
		2. allan 方差曲线 随机过程的方差
		3. allan 方差怎么看[8][9]
	2. 标定结果：噪声、bias 不稳定性

###IMU运动模型：

1. 李代数[4]
	步骤：
	1. gyroscope && accelerometers 运动模型建立
	2. 分离噪声(包含协方差的传播)
	3. 分离bias更新
	4. error对各分量求jacobian(图优化使用，如g2o)

2. 四元数[5]
	1. vins-mono[10] 



参考文档及文献：

[1] An introduction to inertial navigation 

[2] A Robust and Easy to Implement Method for IMU Calibration without External Equipments 

[3] Allan Variance: Noise Analysis for Gyroscopes 

[4] 邱笑晨预积分推导

[5] https://zh.wikipedia.org/zh/%E9%AB%98%E6%96%AF%E8%BF%87%E7%A8%8B

[6] Gaussian Processes for Regression: A Quick Introduction

[7] MEMS陀螺仪中主要噪声源的预测和管理

[8] Stochastic Error Modeling of Smartphone Inertial Sensors
for Navigation in Varying Dynamic Conditions

[9] https://zhuanlan.zhihu.com/p/158927004

[10] VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator