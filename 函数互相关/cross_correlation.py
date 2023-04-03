# /bin/python3
# -*- coding:utf-8 -*-

import numpy as np

def cross_correlation1(x, y):
    result = np.zeros(len(x) + len(y) - 1)
    for i in range(len(x)):
        for j in range(len(y)):
            result[i+j] += x[i] * y[j]
    return result

def cross_correlation(data1, times1, data2, times2, timeoffset):
    size_data1 = data1.shape[0]
    size_data2 = data2.shape[0]
    diff_time_data1 = times1[size_data1 - 1] - times1[0]
    diff_time_data2 = times2[size_data2 - 1] - times2[0]

    count = 0
    max_val = 0
    max_offset = None
    idx_versus_correlation = np.zeros((2 * timeoffset + 1, 2))
    for i in range(-timeoffset, timeoffset, 1):
        corre_val = 0
        for j in range(size_data1):
            index = j + i
            if index < 0:
                continue
            if index >= size_data2:
                continue
            corre_val = corre_val + data1[j] * data2[index]

        if corre_val > max_val:
            max_val = corre_val
            max_offset = i

        idx_versus_correlation[count][0] = i
        idx_versus_correlation[count][1] = corre_val
        count = count + 1

        if max_offset >= 0:
            time_shift = times1[0] - times2[max_offset]
        elif max_offset < 0:
            time_shift = times1[-max_offset] - times2[0]

    return idx_versus_correlation[0:count], max_offset, time_shift

if __name__ == '__main__':

    # 生成测试数据
    data1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    times1 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    data2 = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
    times2 = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # 计算函数互相关
    result, offset, shift = cross_correlation(data1, times1, data2, times2, 5)

    # 输出结果
    print("函数互相关结果：")
    print(result)
    print("时间偏移：", offset)
    print("时间漂移：", shift)
