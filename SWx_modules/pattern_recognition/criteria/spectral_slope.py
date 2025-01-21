"""
spectral_slope.py - Spectral Slope criteria module.

This module defines a class SpectralSlope, which provides methods for computing spectral slope,
sorting a DataFrame, and applying a moving window of spectral slope computations.
"""

import numpy as np
import pandas as pd
import SWx_modules.preprocessing.spectra as spectra

class SpectralSlope:
    """
    Spectral Slope criteria class.

    This class provides methods for computing spectral slope, sorting a DataFrame, and applying
    a moving window of spectral slope computations.
    """

    def __init__(self):
        """
        Initialize the SpectralSlope criteria instance.
        """

    def compute(self, y, **kwargs):
        """
        Compute the spectral slope difference with a reference value.

        Parameters:
        - y (pandas.Series or numpy.ndarray): The input time series or array.
        - df (pandas.DataFrame, optional): The DataFrame for computing the spectral slope.
        - dt (float, optional): Time interval between samples.
        - ref (float, optional): Reference value to subtract from the computed slope.

        Returns:
        - float: The computed spectral slope.
        """
        if 'df' in kwargs:
            df = kwargs['df']
        else:
            df = None
        if 'dt' in kwargs:
            dt = kwargs['dt']
        else:
            dt = 1
        if 'ref' in kwargs:
            ref = kwargs['ref']
        else:
            ref = 0

        # Compute PSD and linear fit for single or multiple signals
        if df is None:
            freq, spec = spectra.psd(y, dt=dt)
            if np.count_nonzero(np.isnan(spec[1:])) < 2 or len(spec) < 3:
                return np.nan
            slope, _ = spectra.linear_fit(np.log(freq[1:]), np.log(spec[1:]))
            return slope - ref
        else:
            tab = df.loc[y.index[0]:y.index[-1]].to_numpy().transpose()
            freq, spec = spectra.psd_vect(tab, dt=dt)
            if np.count_nonzero(np.isnan(spec[1:])) > 2 or len(spec) < 3:
                return np.nan
            slope, _ = spectra.linear_fit(np.log(freq[1:]), np.log(spec[1:]))
            return slope - ref

    def sort(self, df, **kwargs):
        """
        Sort a DataFrame by the absolute values of a specified column.

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

        # Sort the DataFrame by the absolute values of the specified column
        return df.abs().sort_values(by=name_column)

    def moving_application(self, df, **kwargs):
        """
        Apply a moving window of spectral slope computations to a DataFrame.

        Parameters:
        - df (pandas.DataFrame): The DataFrame to apply spectral slope computations to.
        - df_ref (pandas.DataFrame): The reference DataFrame.
        - columns (list, optional): The columns to consider in the computation. 
          If None, all columns are used.
        - dt (float, optional): Time interval between samples.
          If None, the time step of df is used.
        - name_column (str, optional): The name of the output column.

        Returns:
        - pandas.DataFrame: The DataFrame with spectral slope computations applied.

        Remark: set the computed value at the right edge of the window index
        """
        if 'columns' in kwargs:
            columns = kwargs['columns']
        else:
            columns = None
        if 'dt' in kwargs:
            dt = kwargs['dt']
        else:
            dt = None
        if 'name_column' in kwargs:
            name_column = kwargs['name_column']
        else:
            name_column = 'slope'
        if 'df_ref' in kwargs:
            df_ref = kwargs['df_ref']
            length = df_ref.shape[0]
        else:
            df_ref = None
            if 'length' in kwargs:
                length = kwargs['length']
            else:
                raise ValueError('You must provide a reference DataFrame or a length.')

        # Default to using all columns if none specified
        if columns is None:
            columns = df.columns

        # Default to using the time step of the data if none specified
        if dt is None:
            dt = (df.index[1] - df.index[0]).total_seconds()

        # Compute the spectral slope of the reference DataFrame
        if df_ref is None:
            slope_ref = 0
        else:
            slope_ref = self.compute(df_ref, df=df_ref[columns], dt=dt, ref=0)

        # Initialize the output DataFrame
        df_out = pd.DataFrame(columns=[name_column,])

        # Compute spectral slope for each column using a rolling window
        out = df[columns[0]].rolling(length).apply(
            self.compute, kwargs={'df': df[columns], 'dt': dt, 'ref': slope_ref}
        )
        df_out[name_column] = out
        return df_out

def load():
    """
    Load an instance of the SpectralSlope criteria class.

    Returns:
    - SpectralSlope: An instance of the SpectralSlope criteria class.
    """
    # Return an instance of the SpectralSlope class
    return SpectralSlope()
