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

def align_and_sum_stack(stack):
    """
    Given image list or 3D stack, this function uses OpenCV's phase correlation
    to find the shift between images, then apply those offsets and sum the images.

    The first image in the stack is used as the reference.
    """
    # we're going to use OpenCV to do the phase correlation
    # reference slice is first slice
    ref = stack[0]
    shifts = np.array([cv2.phaseCorrelate(ref, _slice) for _slice in stack])
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


#The following is code for making this into a process you can click on in the processing menu

def processing_align_stack(document_controller):
    document_controller.add_processing_operation_by_id(script_id, prefix=_("Aligned sum of "))

def build_menus(document_controller): #makes the Show Color Phase Button
    document_controller.processing_menu.add_menu_item(_("Align image stack"), lambda: processing_align_stack(document_controller))

Application.app.register_menu_handler(build_menus) #called on import to make the Button for this plugin

Operation.OperationManager().register_operation(script_id, lambda: AlignmentOperation())
