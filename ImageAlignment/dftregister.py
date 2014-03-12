# -*- coding: utf-8 -*-
"""
Created on Tue Mar 11 18:26:28 2014

Port of http://www.mathworks.com/matlabcentral/fileexchange/18401-efficient-subpixel-image-registration-by-cross-correlation

@author: Michael Sarahan
"""

import numpy as np

def dftregistration(data1, data2, usfac=1):
    """
    % Efficient subpixel image registration by crosscorrelation. This code
    % gives the same precision as the FFT upsampled cross correlation in a
    % small fraction of the computation time and with reduced memory 
    % requirements. It obtains an initial estimate of the crosscorrelation peak
    % by an FFT and then refines the shift estimation by upsampling the DFT
    % only in a small neighborhood of that estimate by means of a 
    % matrix-multiply DFT. With this procedure all the image points are used to
    % compute the upsampled crosscorrelation.
    % Manuel Guizar - Dec 13, 2007

    % Portions of this code were taken from code written by Ann M. Kowalczyk 
    % and James R. Fienup. 
    % J.R. Fienup and A.M. Kowalczyk, "Phase retrieval for a complex-valued 
    % object by using a low-resolution image," J. Opt. Soc. Am. A 7, 450-458 
    % (1990).

    % Citation for this algorithm:
        % Manuel Guizar-Sicairos, Samuel T. Thurman, and James R. Fienup, 
        % "Efficient subpixel image registration algorithms," Opt. Lett. 33, 
        % 156-158 (2008).

    % Inputs
    % data1    Reference image
    % data2    Image to register 
    % usfac     Upsampling factor (integer). Images will be registered to 
    %           within 1/usfac of a pixel. For example usfac = 20 means the
    %           images will be registered within 1/20 of a pixel. (default = 1)

    % Outputs
    % row_shift col_shift   Pixel shifts between images

    Converted from Matlab to Python by Michael Sarahan, March 2014    
    """
    data1 = np.fft.fft2(data1)
    data2 = np.fft.fft2(data2)
        
    # Whole-pixel shift - Compute crosscorrelation by an IFFT and locate the peak
    m, n = data1.shape
    CC = np.fft.ifft2(data1*data2.conj())
    # Locate maximum
    rloc, cloc = np.unravel_index(np.argmax(CC), CC.shape)
    md2 = np.fix(m/2) 
    nd2 = np.fix(n/2)
    if rloc > md2:
        row_shift = rloc - m
    else:
        row_shift = rloc
    if cloc > nd2:
        col_shift = cloc - n
    else:
        col_shift = cloc
    if usfac == 1:    
        return row_shift, col_shift
    # If upsampling > 1, then refine estimate with matrix multiply DFT
    else:
        # %%% DFT computation %%%
        # % Initial shift estimate in upsampled grid
        row_shift = round(row_shift*usfac)/usfac 
        col_shift = round(col_shift*usfac)/usfac
        usfacceil=np.ceil(usfac*1.5)
        dftshift = np.fix(usfacceil/2) # Center of output array at dftshift+1
        # Matrix multiply DFT around the current shift estimate
        CC = dftups(data2*data1.conj(),usfacceil,usfacceil,usfac,
                    dftshift-row_shift*usfac,dftshift-col_shift*usfac).conj()/(md2*nd2*usfac**2);
        # Locate maximum and map back to original pixel grid 
        rloc, cloc = np.unravel_index(np.argmax(CC), CC.shape)
        rloc = rloc - dftshift;
        cloc = cloc - dftshift;
        row_shift = row_shift + rloc/usfac;
        col_shift = col_shift + cloc/usfac;    

    # If its only one row or column the shift along that dimension has no
    # effect. We set to zero.
    if md2 == 1:
        row_shift = 0;
    if nd2 == 1:
        col_shift = 0
    # output=[error,diffphase,row_shift,col_shift];
    return row_shift, col_shift

def dftups(data, nor=None, noc=None, usfac=1, roff=0, coff=0):
    """
    % Upsampled DFT by matrix multiplies, can compute an upsampled DFT in just
    % a small region.
    % usfac         Upsampling factor (default usfac = 1)
    % [nor,noc]     Number of pixels in the output upsampled DFT, in
    %               units of upsampled pixels (default = size(in))
    % roff, coff    Row and column offsets, allow to shift the output array to
    %               a region of interest on the DFT (default = 0)
    % Recieves DC in upper left corner, image center must be in (1,1) 
    % Manuel Guizar - Dec 13, 2007
    % Modified from dftus, by J.R. Fienup 7/31/06

    % This code is intended to provide the same result as if the following
    % operations were performed
    %   - Embed the array "in" in an array that is usfac times larger in each
    %     dimension. ifftshift to bring the center of the image to (1,1).
    %   - Take the FFT of the larger array
    %   - Extract an [nor, noc] region of the result. Starting with the 
    %     [roff+1 coff+1] element.

    % It achieves this result by computing the DFT in the output array without
    % the need to zeropad. Much faster and memory efficient than the
    % zero-padded FFT approach if [nor noc] are much smaller than [nr*usfac nc*usfac]

    Code translated from Matlab by Michael Sarahan, March 2014
    """
    nr, nc = data.shape
    if nor is None:
        nor = nr
    if noc is None:
        noc = nc
    # Compute kernels and obtain DFT by matrix products
    kernc=np.exp((-1j*2*np.pi/(nc*usfac))*( np.fft.ifftshift(np.arange(nc))[:,np.newaxis] - np.floor(nc/2) ).dot( np.arange(noc)[np.newaxis,:] - coff ))
    kernr=np.exp((-1j*2*np.pi/(nr*usfac))*( np.arange(nor)[:,np.newaxis] - roff ).dot( np.fft.ifftshift(np.arange(nr))[np.newaxis,:] - np.floor(nr/2)  ))
    return kernr.dot(data).dot(kernc)

def shift_image(data, row_shift=0, col_shift=0):
    """
    Shifts input image in Fourier space, effectively wrapping around at boundaries.
    """
    data = np.fft.fft2(data)
    nr, nc = data.shape;
    Nr = np.fft.ifftshift(np.arange(-np.fix(nr/2),np.ceil(nr/2)))
    Nc = np.fft.ifftshift(np.arange(-np.fix(nc/2),np.ceil(nc/2)))
    Nc,Nr = np.meshgrid(Nc,Nr)
    return np.fft.ifft2(data*np.exp(1j*2*np.pi*(-row_shift*Nr/nr-col_shift*Nc/nc))).real