"""
Swift scripting example: image alignment/summation
Purpose: Given a list of images or an image stack, align and
   sum the images.  This is frequently used with a fast scan
   rate to build up an image of a dose-rate-sensitive sample.
Author: Michael Sarahan, Nion, March 2014
"""

# 3rd party library imports
import gettext
import numpy as np

# Nion imports
from nion.imaging import Operation
from nion.swift import Application

# Imports from any modules you make


# for translation
_ = gettext.gettext  

# This should be a unique identifier for your process.  Try to be descriptive, but not generic (don't conflict with other plugins)
script_id = _("your-process-operation")
# this is the text that the menu will display
process_description = _("Process operation")
# The prefix to prepend to the result image name:
process_prefix = _("Your process done to ")

# you can define any functions to be used in your processing here.  
# They do not need to be defined in the class itself.  
# By defining them here, you can debug them more easily by directly importing them into your testing environment.
def your_processing_function(data, parameter1=None):
    return data

# From here down, we're using a standard layout so that Swift knows how to execute your process.
# the most important part is the process method, which is where you'll need to add calls to your processing function(s).

class ProcessOperation(Operation.Operation):
    """
    A Swift plugin for you to use.
    """
    def __init__(self):
        super(ProcessOperation, self).__init__(process_description, script_id)

    def process(self, data):
        """
        Swift calls this method when you click on the menu entry for this process,
        and also whenever the parameters for this process or the underlying data change.
        
        This is where you'll call your methods to actually operate on the data.
        This method should always return a new copy of data
        """
        return your_processing_function(data)
    
    def get_processed_data_shape_and_dtype(self, data_shape, data_dtype):
        """
        Swift needs to know how your process changes the data type and shape, if it changes these.
        If you don't change the data type nor shape, you can delete this method.
        
        The input parameters are the original input data shape and type.
        The return parameters should be the processed data shape and dtype (in that order!)
        """
        return data_shape[1:], data_dtype  
    
    def get_processed_spatial_calibrations(self, data_shape, data_dtype, spatial_calibrations):
        """
        Swift needs to know how your process changes the data type and shape, if it changes these.
        If you don't change calibrations (no new axes, no removed axes), you can just delete this method.
        
        
        The input parameters are the original input data shape, type, and list of calibrations
        The return parameters should be the list of calibrations for the processed data.
        """
        return spatial_calibrations


# The following is code for making this into a menu entry on the processing menu.  You don't need to change it.

def build_menus(document_controller): # makes the menu entry for this plugin
    operation_callback = lambda : document_controller.add_processing_operation_by_id(script_id, prefix=process_prefix)
    document_controller.processing_menu.add_menu_item(_("Align image stack"), operation_callback)

Application.app.register_menu_handler(build_menus) # called on import to make the menu entry for this plugin
Operation.OperationManager().register_operation(script_id, lambda: ProcessOperation())