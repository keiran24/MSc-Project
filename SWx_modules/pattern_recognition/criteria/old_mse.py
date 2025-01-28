"""
mse.py - Mean Squared Error (MSE) criteria module.

This module defines a class MSE, which provides methods for computing MSE, sorting a DataFrame,
and applying a moving window of MSE computations.
"""

import numpy as np
import pandas as pd

class MSE:
    """
    Mean Squared Error (MSE) criteria class.

    This class provides methods for computing MSE, sorting a DataFrame, and applying a moving
    window of MSE computations.
    """

    def __init__(self):
        """
        Initialize the MSE criteria instance.
        """

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
            return np.nan
            #raise ValueError("The length of y and y_ref must be the same.")

        # Compute the Mean Squared Error (MSE)
        out = np.nanmean((y - y_ref)**2, axis=0)
        #print(y,y_ref,out)
        return out

    def sort(self, df, **kwargs):
        """
        Sort a DataFrame by a specified column.

        Parameters:
        - df (pandas.DataFrame): The DataFrame to be sorted.
        - name_column (str): The name of the column used for sorting.

        Returns:
        - pandas.Index: The sorted index.
        """
        if 'name_column' in kwargs:
            name_column = kwargs['name_column']
        else:
            name_column = df.columns[0] 

        # Sort the DataFrame by the specified column
        return df.sort_values(by=name_column)

    def moving_application(self, df, **kwargs):
        """
        Apply a moving window of MSE computations to a DataFrame.

        Parameters:
        - df (pandas.DataFrame): The DataFrame to apply MSE computations to.
        - df_ref (pandas.DataFrame): The reference DataFrame.

        Returns:
        - pandas.DataFrame: The DataFrame with MSE computations applied.

        Remark: set the computed value at the right edge of the window index
        """
        if 'columns' in kwargs:
            columns = kwargs['columns']
        else:
            columns = None
        if 'df_ref' in kwargs:
            df_ref = kwargs['df_ref']
        else:
            raise ValueError('You must provide a reference DataFrame.')
        if 'nanprop' in kwargs:
            nanprop = kwargs['nanprop']
        else:
            nanprop = 0.8

        # If columns are not provided, use all columns
        if columns is None:
            columns = df_ref.columns
        # Set the length of the moving window
        length = df_ref.shape[0]

        if 'step' in kwargs:
            step = length//kwargs['step']
        else: step = 1


        df_out = pd.DataFrame(columns=columns)
        # Compute MSE for each column using a rolling window
        min_periods = int(nanprop*len(df_ref.index))
        for col in columns:
            df_out[col] = df[col].rolling(length,min_periods=min_periods,step=step).apply(
                self.compute, raw=True, kwargs={'y_ref': df_ref[col].values})
        return df_out

def load():
    """
    Load an instance of the MSE criteria class.

    Returns:
    - MSE: An instance of the MSE criteria class.
    """
    # Return an instance of the MSE class
    return MSE()
