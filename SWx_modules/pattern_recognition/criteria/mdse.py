"""
mse.py - Mean Squared Error (MSE) criteria module.

This module defines a class MSE, which provides methods for computing MSE, sorting a DataFrame,
and applying a moving window of MSE computations.
"""

import numpy as np
import pandas as pd
from SWx_modules.pattern_recognition.criteria.mse import MSE

class MdSE(MSE):
    """
    Mean Squared Error (MSE) criteria class.

    This class provides methods for computing MSE, sorting a DataFrame, and applying a moving
    window of MSE computations.
    """

    def __init__(self):
        """
        Initialize the MSE criteria instance.
        """
        super(MdSE, self).__init__()

    def compute(self, y, **kwargs):
        """
        Compute the Mean Squared Error (MSE) between two arrays.

        Parameters:
        - y (numpy.ndarray): The array to be compared.
        - y_ref (numpy.ndarray, optional): The reference array. If None, it's set to zeros.

        Returns:
        - numpy.ndarray: The computed MSE.
        """
        #print("ici",y,kwargs)
        if 'y_ref' in kwargs:
            y_ref = kwargs['y_ref']
        else:
            y_ref = None

        # If reference array is not provided, set it to zeros
        if y_ref is None:
            y_ref = y * 0

        # Check if the lengths of y and y_ref are the same
        if len(y_ref) != len(y):
            raise ValueError("The length of y and y_ref must be the same.")

        # Compute the Mean Squared Error (MSE)
        out = np.nanmedian((y - y_ref)**2, axis=0)
        #print(y,y_ref,out)
        return out

def load():
    """
    Load an instance of the MSE criteria class.

    Returns:
    - MSE: An instance of the MSE criteria class.
    """
    # Return an instance of the MSE class
    return MdSE()
