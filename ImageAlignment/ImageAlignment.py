"""
Swift scripting example: image alignment/summation
Purpose: Given a list of images or an image stack, align and
   sum the images.  This is frequently used with a fast scan
   rate to build up an image of a dose-rate-sensitive sample.
Author: Michael Sarahan, Nion, March 2014
"""

import cv2
import gettext
import numpy as np

from nion.imaging import Operation
from nion.swift import Application

_ = gettext.gettext  # for translation

script_id = _("align-image-stack-operation")

def blur(image, blur_size=7):
    return cv2.GaussianBlur(image, (blur_size, blur_size),3)

def edge_filter(image):
    vertical=cv2.Scharr(image, -1, 0, 1)
    horizontal=cv2.Scharr(image, -1, 1, 0)
    return np.sqrt(vertical**2+horizontal**2)

def align_and_sum_stack(stack, blur_image=True, edge_filter_image=False):
    """
    Given image list or 3D stack, this function uses OpenCV's phase correlation
    to find the shift between images, then apply those offsets and sum the images.

    The first image in the stack is used as the reference.
    """
    # Pre-allocate an array for the shifts we'll measure
    shifts=np.zeros((stack.shape[0],2))
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
        shifts[index] = ref_shift+np.array(cv2.phaseCorrelate(ref, filtered_slice))
        ref=filtered_slice[:]
        ref_shift=shifts[index]
    # round to nearest integer coordinate (subpixel registration would require
    #     supersampling input and output data to desired precision)
    shifts = shifts.round()
    # subtract the minimum, so that our space still starts at (0,0),
    #   not a negative number
    shifts -= shifts.min(axis=0)
    # get the maximum offset
    maxima = shifts.max(axis=0)
    # sum image needs to be big enough for shifted images
    sum_image = np.zeros((ref.shape[0] + maxima[0], ref.shape[1] + maxima[1]))
    # add the images to the registered stack
    for index, _slice in enumerate(stack):
        sum_image[shifts[index, 0]:shifts[index, 0] + ref.shape[0],
                  shifts[index, 1]:shifts[index, 1] + ref.shape[1]] += _slice
    return sum_image

class AlignmentOperation(Operation.Operation):
    """
    A Swift plugin for image alignment and summation.
    """
    def __init__(self):
        super(AlignmentOperation, self).__init__(_("Align Image Stack"), script_id)

    def process(self, stack):
        """
        Given image list or 3D stack, this function uses OpenCV's phase correlation
        to find the shift between images, then apply those offsets and sum the images.

        The first image in the stack is used as the reference.
        """
        return align_and_sum_stack(stack)
    
    def get_processed_data_shape_and_dtype(self, data_shape, data_dtype):
        # since we sum over the first dimension, we change the shape to be just the later dimensions
        # data type does not change - return it
        return data_shape[1:], data_dtype  
    
    def get_processed_spatial_calibrations(self, data_shape, data_dtype, spatial_calibrations):
        # since we sum over the first dimension, we lose it as a dimension.  Omit it from the spatial_calibrations
        return spatial_calibrations[1:]


#The following is code for making this into a process you can click on in the processing menu

def processing_align_stack(document_controller):
    document_controller.add_processing_operation_by_id(script_id, prefix=_("Aligned sum of "))

def build_menus(document_controller): # makes the menu entry for this plugin
    document_controller.processing_menu.add_menu_item(_("Align image stack"), lambda: processing_align_stack(document_controller))

Application.app.register_menu_handler(build_menus) # called on import to make the Button for this plugin

Operation.OperationManager().register_operation(script_id, lambda: AlignmentOperation())

if __name__=="__main__":
    # fake data stack
    data = np.random.random((20, 100, 100))
    sum_image = align_and_sum_stack(data)
    # TODO: define meaningful tests of sum data
    print sum_image