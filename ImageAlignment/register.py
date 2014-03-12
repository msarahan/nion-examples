# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 11:13:51 2014

@author: Michael
"""

import cv2
import numpy as np
import scipy as sp

import dftregister

def blur(image, blur_size=7):
    return cv2.GaussianBlur(image, (blur_size, blur_size),3)

def edge_filter(image):
    vertical=cv2.Scharr(image, -1, 0, 1)
    horizontal=cv2.Scharr(image, -1, 1, 0)
    return np.sqrt(vertical**2+horizontal**2)

def align_and_sum_stack(stack, blur_image=True, edge_filter_image=False,
                        interpolation_factor=100):
    """
    Given image list or 3D stack, this function uses cross correlation and Fourier space supersampling
    to find the shift between images, then apply those offsets and sum the images.
    """
    # Pre-allocate an array for the shifts we'll measure
    shifts=np.zeros((stack.shape[0], 2))
    # we're going to use OpenCV to do the phase correlation
    # initial reference slice is first slice
    ref=stack[0][:]
    if blur_image:
        ref=blur(ref)
    if edge_filter_image:
        ref=edge_filter(ref)
    ref_shift=np.array([0,0])
    for index, _slice in enumerate(stack):
        filtered_slice=_slice[:]
        if blur_image:
            filtered_slice=blur(filtered_slice)
        if edge_filter_image:
            filtered_slice=edge_filter(filtered_slice)
        shifts[index] = ref_shift+np.array(dftregister.dftregistration(ref, 
                                        filtered_slice,interpolation_factor))
        ref=filtered_slice[:]
        ref_shift=shifts[index]
    # sum image needs to be big enough for shifted images
    sum_image = np.zeros(ref.shape)
    # add the images to the registered stack
    for index, _slice in enumerate(stack):
        sum_image += dftregister.shift_image(_slice, shifts[index,0], shifts[index,1])
    return sum_image