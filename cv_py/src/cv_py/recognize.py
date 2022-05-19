#!/usr/bin/env python3
import cv2 as cv
import numpy as np
import cv_py.image
from typing import Sequence

"""
    尚未定型

    功能:
    幾何辨識
"""

def average_point(*points_: Sequence['int | float']) -> np.ndarray:
    '''
        用途:
        將多個座標點平均起來

        參數 *points_: 一系列座標點.
    '''
    points = np.array(points_)
    return points.mean(axis=0)

def simple_line_check(contour_: np.ndarray, threshold_: 'int | float',
                      image_: np.ndarray=None) -> bool:
    '''
        用途:
        以角度檢測輪廓方向是否成直線.

        參數 contour_: 輪廓, 只能為單個輪廓.
        參數 threshold_: 最小角度差.
        參數 image_: 影像, 可將旋轉矩形之結果繪製至該影像.
    '''
    rect = cv.boundingRect(contour_)
    mask = np.zeros((rect[3], rect[2]), np.uint8)
    cv.drawContours(mask, [contour_], -1, 255, -1, offset=(-rect[0], -rect[1]))
    roi_1, roi_2 = cv_py.image.slice_half(mask, cv_py.image.SLICE.SLICE_SHORTEST)

    contour_1, _ = cv.findContours(roi_1, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contour_2, _ = cv.findContours(roi_2, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    angle_1 = cv.minAreaRect(contour_1[0])[2]
    angle_2 = cv.minAreaRect(contour_2[0])[2]
    if image_ is not None:
        rotate_1 = cv.minAreaRect(contour_1[0])
        rotate_2 = cv.minAreaRect(contour_2[0])
        box_1 = np.int0(cv.boxPoints(rotate_1))
        box_2 = np.int0(cv.boxPoints(rotate_2))
        if rect[2] >= rect[3]:
            offset = rect[0] + int(rect[2]/2), rect[1]
        else:
            offset = rect[0], rect[1] + int(rect[3]/2)
        cv.drawContours(image_, [box_1], -1, (0, 255, 0), 3, offset=(rect[0], rect[1]))
        cv.drawContours(image_, [box_2], -1, (255, 255, 0), 3, offset=offset)

    if angle_1 <= threshold_ and angle_2 >= 90-threshold_:
        if 90-angle_2+angle_1 > threshold_:
            return False

        return True

    if angle_2 <= threshold_ and angle_1 >= 90-threshold_:
        if 90-angle_1+angle_2 > threshold_:
            return False

        return True

    if abs(angle_1-angle_2) > threshold_:
        return False

    return True