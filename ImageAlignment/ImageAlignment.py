"""
Swift scripting example: image alignment/summation
Purpose: Given a list of images or an image stack, align and
   sum the images.  This is frequently used with a fast scan
   rate to build up an image of a dose-rate-sensitive sample.
Author: Michael Sarahan, Nion, March 2014
"""

import gettext

from nion.imaging import Operation
from nion.swift import Application

# implementation of processing functionality defined in register.py
import register

_ = gettext.gettext  # for translation

# This should be a unique identifier for your process.  Try to be descriptive, but not generic (don't conflict with other plugins)
script_id = _("align-image-stack-operation")
# this is the text that the menu will display
process_name = _("Align Image Stack")
# The prefix to prepend to the result image name:
process_prefix = _("Aligned sum of ")

class AlignmentOperation(Operation.Operation):
    """
    A Swift plugin for image alignment and summation.
    """
    def __init__(self):
        super(AlignmentOperation, self).__init__(process_name, script_id)

    def process(self, stack):
        """
        Given image list or 3D stack, this function uses OpenCV's phase correlation
        to find the shift between images, then apply those offsets and sum the images.

        The first image in the stack is used as the reference.
        """
        return register.align_and_sum_stack(stack)
    
    def get_processed_data_shape_and_dtype(self, data_shape, data_dtype):
        # since we sum over the first dimension, we change the shape to be just the later dimensions
        # data type does not change - return it
        return data_shape[1:], data_dtype  
    
    def get_processed_spatial_calibrations(self, data_shape, data_dtype, spatial_calibrations):
        # since we sum over the first dimension, we lose it as a dimension.  Omit it from the spatial_calibrations
        return spatial_calibrations[1:]


#The following is code for making this into a process you can click on in the processing menu

def build_menus(document_controller): # makes the menu entry for this plugin
    process_callback = lambda: document_controller.add_processing_operation_by_id(script_id, prefix=process_prefix)
    document_controller.processing_menu.add_menu_item(process_name, process_callback(document_controller))

Application.app.register_menu_handler(build_menus) # called on import to make the Button for this plugin

Operation.OperationManager().register_operation(script_id, lambda: AlignmentOperation())
