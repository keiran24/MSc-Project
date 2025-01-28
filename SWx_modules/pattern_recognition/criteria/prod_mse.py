"""
mse.py - Mean Squared Error (MSE) criteria module.

This module defines a class MSE, which provides methods for computing MSE, sorting a DataFrame,
and applying a moving window of MSE computations.
"""

import pandas as pd

from SWx_modules.pattern_recognition.criteria.mse import MSE

class ProdMSE (MSE):
    """
    Product of Mean Squared Error (MSE) of multiple columns criteria class.

    This class provides methods for computing the product of MSE of multiple columns, 
    sorting a DataFrame, and applying a moving window of MSE computations.
    """

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
        df_out = super(ProdMSE,self).moving_application(df, **kwargs)
        columns = df_out.columns
        df_out['prod_MSE'] = df_out.prod(axis='columns')
        df_out = df_out.drop(columns=columns)
        return df_out

def load():
    """
    Load an instance of the MSE criteria class.

    Returns:
    - MSE: An instance of the MSE criteria class.
    """
    # Return an instance of the MSE class
    return ProdMSE()
