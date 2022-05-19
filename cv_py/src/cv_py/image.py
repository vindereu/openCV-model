#!/usr/bin/env python3
import cv2 as cv
import numpy as np
from enum import IntEnum

"""
    尚未定型

    功能:
    影像操作和輪廓分析.

    未來可能加入之功能:
    1. 最大輪廓考慮輪廓等級
"""

class SLICE(IntEnum):
    '''
        用途:
        定義影像裁切方向, 和slice(), slice_half()做搭配.
    '''
    SLICE_HORIZONTAL = 0
    SLICE_VERTICAL = 1
    SLICE_SHORTEST = 2
    SLICE_LONGEST = 3

def largest_contour(contours_: np.ndarray , area_threshold_: 'int | float'=0,
                         number_found_: int=1) -> 'tuple[int]':
    '''
        用途:
        找尋前幾個像素面積最大的輪廓, 並返回其索引值, 若面積為空, 則回傳None.

        參數 contours_: 輪廓, 可為單個或多個.
        參數 area_threshold_: 輪廓最小容許面積.
        參數 number_found_: 返回的最大輪廓數量, 小於1則不限制數量.
    '''
    if not contours_:
        return None

    contour_info = np.array([0, 0])
    isContour = False
    for i, contour in enumerate(contours_):
        area = cv.contourArea(contour)
        if area >= area_threshold_:
            contour_info = np.vstack((contour_info, (i, area)))
            isContour = True
    
    contour_info = np.delete(contour_info, 0, axis=0)

    if not isContour:
        return None
    
    largest_contour_index = np.array([], dtype=int)
    if number_found_ > 0:
        while contour_info.size and number_found_ > 0:
            largest_area = contour_info.max(axis=0)[1]
            largest_area_index = int(contour_info.flatten().tolist().index(largest_area) / 2)
            largest_contour_index = np.hstack((largest_contour_index,
                                               (int(contour_info[largest_area_index][0]))))
            contour_info = np.delete(contour_info, largest_area_index, axis=0)
            number_found_ -= 1

    else:
        while contour_info.size:
            largest_area = contour_info.max(axis=0)[1]
            largest_area_index = int(contour_info.flatten().tolist().index(largest_area) / 2)
            largest_contour_index = np.hstack((largest_contour_index,
                                               (int(contour_info[largest_area_index][0]))))
            contour_info = np.delete(contour_info, largest_area_index, axis=0)

    return tuple(largest_contour_index.tolist())

def slice(img_: np.ndarray, index_: int, direction_: SLICE) -> 'tuple[np.ndarray, np.ndarray]':
    '''
        用途:
        將影像裁切成2部分.

        參數 img_: 輸入影像.
        參數 index_: 裁切位置索引.
        參數 direction_: 裁切方向, 選項:水平或垂直.
    '''
    if direction_ == SLICE.SLICE_HORIZONTAL:
        return img_[:index_, :], img_[index_:, :]
    if direction_ == SLICE.SLICE_VERTICAL:
        return img_[:, :index_], img_[:, index_:]

def slice_half(img_: np.ndarray, direction_: SLICE) -> 'tuple[np.ndarray, np.ndarray]':
    '''
        用途:
        將影像對半裁切.

        參數 img_: 輸入影像
        參數 direction_: 裁切方向, 選項:影像短邊、影像長邊、水平、垂直.
    '''
    if direction_ == SLICE.SLICE_LONGEST:
        if img_.shape[0] >= img_.shape[1]:
            return slice(img_, int(img_.shape[1]/2), SLICE.SLICE_VERTICAL)

        return slice(img_, int(img_.shape[0]/2), SLICE.SLICE_HORIZONTAL)

    if direction_ == SLICE.SLICE_SHORTEST:
        if img_.shape[0] <= img_.shape[1]:
            return slice(img_, int(img_.shape[1]/2), SLICE.SLICE_VERTICAL)

        return slice(img_, int(img_.shape[0]/2), SLICE.SLICE_HORIZONTAL)

    if direction_ == SLICE.SLICE_HORIZONTAL:
        index = int(img_.shape[0]/2)
        return img_[:index, :], img_[index:, :]

    if direction_ == SLICE.SLICE_VERTICAL:
        index = int(img_.shape[1]/2)
        return img_[:, :index], img_[:, index:]
