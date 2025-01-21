"""
spectra.py - Module for computing Power Spectral Density and linear fits.

This module provides functions for computing the Power Spectral Density (PSD) of a signal,
performing linear fits on given data, and computing the PSD of a multidimensional signal.

Functions:
- PSD(signal, dt=1):
    Compute the Power Spectral Density (PSD) of a signal.

- linear_fit(x, y):
    Perform a linear fit on the given data.

- PSD_vect(signal_vect, dt=1):
    Compute the PSD of a multidimensional (vectorial) signal sampled at a specified scale.
"""

import numpy as np
from scipy import stats

def psd(signal, dt=1):
    """
    Compute the Power Spectral Density (PSD) of a signal.

    Parameters:
    - signal (numpy.ndarray): The input signal.
    - dt (float, optional): Time interval between samples.

    Returns:
    - numpy.ndarray, numpy.ndarray: The frequency range and the corresponding PSD.
    """
    # Check for NaN values in the signal
    if np.count_nonzero(np.isnan(signal)) > len(signal) - 2:
        return np.array([np.nan, ] * (len(signal) // 2)), np.array([np.nan, ] * (len(signal) // 2))

    # Remove the mean from the signal
    y = signal - np.nanmean(signal)
    yi = np.arange(len(y))
    mask = np.isfinite(y)

    # Interpolate NaN values in the signal
    yfiltered = np.interp(yi, yi[mask], y[mask])

    # Compute the Power Spectral Density using the Fast Fourier Transform
    spectra = np.power(np.abs(np.fft.rfft(yfiltered)), 2) * dt / len(signal) * 2
    spectra[0] /= 2

    # Compute the frequency range
    range_freq = np.fft.rfftfreq(len(signal), d=dt)[:len(spectra)]
    return range_freq, spectra

def linear_fit(x, y):
    """
    Perform a linear fit on the given data.

    Parameters:
    - x (numpy.ndarray): The x-values of the data.
    - y (numpy.ndarray): The y-values of the data.

    Returns:
    - float, float: The slope and intercept of the linear fit.
    """
    # Check for empty input arrays
    if len(x) < 1 or len(y) < 1:
        return np.nan, np.nan

    # Perform linear regression using scipy.stats.linregress
    res = stats.linregress(x, y)
    return res.slope, res.intercept

def psd_vect(signal_vect, dt=1):
    """
    Compute the PSD of a multidimensional (vectorial) signal sampled at a specified scale.

    Parameters:
    - signal_vect (numpy.ndarray): The 1D vectorial signal.
    - dt (float, optional): Time interval between samples.

    Returns:
    - numpy.ndarray, numpy.ndarray: The frequency range and the corresponding PSD.
    """
    # Compute PSD for the first component of the vectorial signal
    range_freq, spectra = psd(signal_vect[0], dt=dt)

    # Accumulate PSDs for the remaining components of the vectorial signal
    for i in range(1, len(signal_vect)):
        spectra += psd(signal_vect[i], dt=dt)[1]

    return range_freq, spectra
