#!/usr/bin/env python3
import cv2 as cv
import numpy as np
from typing import Sequence

"""
    尚未定型

    功能:
    影像模糊處理與形態學處理
"""

def bilateral(src, distance: int, sigma_color: int, sigma_space: int):
    bilate = cv.bilateralFilter(src, distance, sigma_color, sigma_space)
    return bilate

def blur(src: np.ndarray, k_size: int):
    kernel_aver = k_size, k_size
    average = cv.blur(src, kernel_aver)
    return average

def convolution(src: np.ndarray, k_size: int):
    kernel_conv = np.ones((k_size, k_size)) / k_size ** 2
    convolution = cv.filter2D(src, -1, kernel_conv)
    return convolution

def gaussian(src: np.ndarray, k_size: int, sigmaX: float=0, sigmaY: float=0):
    gauss_blur = cv.GaussianBlur(src, (k_size,)*2, sigmaX, sigmaY)
    return gauss_blur

def median(src: np.ndarray, k_size: int):
    median = cv.medianBlur(src, k_size)
    return median

def morph(img_: 'np.ndarray', method_: 'int | Sequence',
                kernel_size_: 'int | Sequence',
                kernel_shape_: 'int | Sequence' = cv.MORPH_RECT,
                iterations: int=1) -> np.ndarray:
    '''
        用途:
        以給定順序、方法和內核大小對影像做多次型態學處理.

        參數 img_: 輸入影像.
        參數 method_: 影像處理方式.
        參數 kernel_size_: 內核大小.
        參數 kernel_shape_: 內核形狀, 預設為cv.MORPH_RECT.
        參數 iterations: 執行次數, 預設為1
    '''
    isSequence = True
    isInt = True
    for param in (method_, kernel_size_, kernel_shape_):
        if not isinstance(param, Sequence):
            isSequence = False
        elif not isinstance(param, int):
            isInt = False
    
    if not (isSequence or isInt):
        raise TypeError("All types of the last 3 params should be int or Sequence.")
    elif isSequence:
        if len(method_) != len(kernel_size_) or len(method_) != len(kernel_size_):
            print(len(method_), len(kernel_size_), len(kernel_shape_))
            raise ValueError("Inconsistent amount of input data")

        for option, size, shape in zip(method_, kernel_size_, kernel_shape_):
            kernel = cv.getStructuringElement(shape, (size,)*2)
            img = cv.morphologyEx(img_, option, kernel, iterations=iterations)
    
    else:
        kernel = cv.getStructuringElement(kernel_shape_, (kernel_size_,)*2)
        img = cv.morphologyEx(img_, method_, kernel, iterations=iterations)

    return img