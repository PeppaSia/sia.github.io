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
        print(f'y信号移动{t},自相关值为{result}')
        if result > max_res:
            max_res = result
            offset = t
    return offset, max_res


if __name__ == '__main__':
    x = [5, 6, 0]
    y = [5, 6, 0]
    offset, max_res = cross_correlation1(x, y)
    print(f'y信号移动{offset},自相关值最大，最大为{max_res}')
