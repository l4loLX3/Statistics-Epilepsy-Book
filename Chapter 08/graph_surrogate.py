"""
Functions for computing surrogate time-series.

Created by: Ankit Khambhati

2023-03-30
"""

import numpy as np

def uniform_shuffle(xV, fixed_order=True):
    """
    Uniform shuffling of time-series signal amplitudes. 
    Preserves shape of amplitude distribution. 
    Disrupts temporal ordering and autocorrelation.

    Parameters
    ----------
        xV: ndarray, shape (T, N)
            Time-series with T samples and N nodes.

        fixed_order: bool
            Preserve the shuffling order across nodes. 

    Returns
    -------
        zM: ndarray, shape (T, N)
            Surrogate of the input time-series.
    """
    T, N = xV.shape
    if fixed_order:
        return xV[np.random.permutation(T)]
    else:      
        return np.array([np.random.permutation(x)
                         for x in xV.T]).T

def fourier_constrained_shuffle(xV, fixed_phase=True):
    """
    Amplitude Adjusted Fourier Transform Surrogates

    This code is based on the following MATLAB code

    <AAFTsur.m>, v 1.0 2010/02/11 22:09:14  Kugiumtzis & Tsimpiris
    This is part of the MATS-Toolkit http://eeganalysis.web.auth.gr/

    Copyright (C) 2010 by Dimitris Kugiumtzis and Alkiviadis Tsimpiris
                           <dkugiu@gen.auth.gr>

    Reference : D. Kugiumtzis and A. Tsimpiris, "Measures of Analysis of Time
                Series (MATS): A Matlab  Toolkit for Computation of Multiple
                Measures on Time Series Data Bases", Journal of Statistical
                Software, 2010

    The original python author was: https://github.com/lneisenman/aaft

    Parameters
    ----------
        xV: ndarray, shape (T, N)
            Time-series with T samples and N nodes.

        fixed_phase: bool
            Preserve the phase shuffling order across nodes. 

    Returns
    -------
        zM: ndarray, shape (T, N)
            Surrogate of the input time-series.
    """        
    
    zM = np.zeros_like(xV)
    rfiV = None
    
    for ii, xV_ in enumerate(xV.T):
        # Standard param checks
        n = len(xV_)
        T = np.argsort(xV_)
        oxV = np.sort(xV_)
        ixV = np.argsort(T)

        # Rank order a white noise time series 'wV' to match the ranks of 'xV'
        wV = np.random.randn(n) * np.std(xV_, ddof=1)    # match Matlab std
        owV = np.sort(wV)
        yV = owV[ixV].copy()

        # Fourier transform, phase randomization, inverse Fourier transform
        n2 = n//2
        tmpV = np.fft.fft(yV, 2*n2)
        magnV = np.abs(tmpV)
        fiV = np.angle(tmpV)
        if fixed_phase: 
            if rfiV is None:
                rfiV = np.random.rand(n2-1) * 2 * np.pi
        else:
            rfiV = np.random.rand(n2-1) * 2 * np.pi
        nfiV = np.append([0], rfiV)
        nfiV = np.append(nfiV, fiV[n2+1])
        nfiV = np.append(nfiV, -rfiV[::-1])
        tmpV = np.append(magnV[:n2+1], magnV[n2-1:0:-1])
        tmpV = tmpV * np.exp(nfiV * 1j)
        yftV = np.real(np.fft.ifft(tmpV, n))  # Transform back to time domain

        # Rank order the 'xV' to match the ranks of the phase randomized
        # time series
        T2 = np.argsort(yftV)
        iyftV = np.argsort(T2)
        zM[:, ii] = oxV[iyftV]  # the AAFT surrogate of xV
        
    return zM