# /bin/python3
# -*- coding:utf-8 -*-
import numpy as np


def cross_correlation1(x, y):
    print('x:', x)
    print('y:', y)
    m, n = len(x), len(y)
    offset_range = max(m, n)
    offset = None
    max_res = -1000
    for t in range(-offset_range, offset_range, 1):
        result = 0
        for i in range(m):
            index = t + i
            if index < 0:
                continue
            if index >= n:
                continue
            # print(t, i, index, x[i], y[index], x[i] * y[index])
            result = result + x[i] * y[index]
        print(t, result)
        if result > max_res:
            max_res = result
            offset = t
    return offset, max_res


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
            print(i, j, index, data1[j] * data2[index])
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
    x = [5, 6, 7, 0, 0, 0]
    y = [5, 6, 7, 0, 0, 0]
    print(cross_correlation1(x, y))
