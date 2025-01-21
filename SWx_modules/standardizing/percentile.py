"""
mean_std.py - Mean Std standardization module.

This module defines a class MeanStd, which provides methods for computing the 
Mean Std standardization.
"""
import numpy as np
from SWx_modules.standardizing.conversion import Conversion

class Percentile(Conversion):
    """
    Mean Std standardization class.

    This class provides methods for computing the Mean Std standardization.
    """

    def __init__(self, **kwargs):
        """
        Initialize the MeanStd standardization instance.
        """
        super(Percentile, self).__init__()
    
    def set_attributes(self, **kwargs):
        """
        Set the attributes of the MeanStd standardization instance.
        """
        self.set_conversion_matrix(**kwargs)

    def get_percentile_rank(self, df, columns=None, na_level=None, **kwargs,):
        """
        Calculate the percentile rank for columns in a DataFrame.

        Parameters:
        - df (pd.DataFrame): The input DataFrame.
        - columns (list, optional): Columns to calculate percentile ranks. 
        If None, all numeric columns are used.
        - na_level (float, optional): Value to fill NaN values after percentile rank calculation.
        - kwargs (dict, optional): Additional keyword arguments for the rank method.

        Returns:
        - pd.DataFrame: DataFrame with percentile ranks.
        """

        if columns is None:
            if 'numeric_only' not in kwargs:
                kwargs['numeric_only'] = True
                columns = df.select_dtypes(include=np.number).columns
            else:
                columns = df.columns
        if 'method' not in kwargs:
            kwargs['method'] = 'average'
        if 'na_option' not in kwargs:
            kwargs['na_option'] = 'keep'
        df_out = df.copy()
        for col in columns:
            df_out[col] = df[col].rank(pct=True, **kwargs).apply(lambda x: x * 100)
        if na_level is not None:
            df_out = df_out.fillna(na_level)
        return df_out

    def set_conversion_matrix(self, df_physical=None, df_standard=None, **kwargs):
        """
        Create a conversion dictionary between original values and standardized values.

        Parameters:
        - df (pd.DataFrame): The input DataFrame.
        - columns (list, optional): Columns to standardize. If None, all numeric columns are used.

        Returns:
        - dict: Conversion dictionary between original values and standardized values.
        """
        if 'conversion_matrix' in kwargs:
            self.conversion_matrix = kwargs['conversion_matrix']
            return None

        if df_physical is None and df_standard is None:
            raise ValueError("You must provide at least df_physical or the conversion matrix.")
        elif df_standard is None:
            df = df_physical
        else:
            super(Percentile, self).set_conversion_matrix(df_physical, df_standard, **kwargs)
            return None

        # Get the optional arguments
        if 'columns' in kwargs:
            columns = kwargs['columns']
        else:
            columns = None

        # Initialise the optional arguments
        if columns is None:
            columns = df.columns

        df_standard = self.get_percentile_rank(df, **kwargs)
        super(Percentile, self).set_conversion_matrix(df_physical, df_standard, **kwargs)
        return None

    def standardize(self, df_physical, **kwargs):
        """
        Standardize the columns of a DataFrame using mean and standard deviation.

        Parameters:
        - df (pd.DataFrame): The input DataFrame.
        - columns (list, optional): Columns to standardize. If None, all numeric columns are used.

        Returns:
        - pd.DataFrame: Standardized DataFrame.
        - pd.DataFrame: Summary statistics (mean and std) of the standardized columns.
        """
        df_out = self.get_percentile_rank(df_physical, **kwargs)
        return df_out

def load():
    """
    Load an instance of the MSE criteria class.

    Returns:
    - Percentile: An instance of the Percentile standardization class.
    """
    # Return an instance of the MSE class
    return Percentile()
