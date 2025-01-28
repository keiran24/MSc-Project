"""
mean_std.py - Mean Std standardization module.

This module defines a class MeanStd, which provides methods for computing the 
Mean Std standardization.
"""

import pandas as pd
from SWx_modules.standardizing.conversion import Conversion

class Max(Conversion):
    """
    Mean Std standardization class.

    This class provides methods for computing the Mean Std standardization.
    """

    def __init__(self, **kwargs):
        """
        Initialize the MeanStd standardization instance.
        """
        super(Max, self).__init__()
        try:
            self.set_attributes(**kwargs)
        except ValueError:
            self.max = None
    
    def set_attributes(self, **kwargs):
        """
        Set the attributes of the MeanStd standardization instance.
        """
        try: 
            super(Max, self).set_attributes(**kwargs)
        except ValueError:
            self.conversion_matrix = None

        if 'describe' in kwargs:
            self.max = {col:max(kwargs['describe'].loc['min',col], 
                                kwargs['describe'].loc['max',col]) for col in kwargs['describe'].columns}

        elif 'max' in kwargs:
            if isinstance(kwargs['max'], dict):
                self.max = kwargs['max']
            elif ((isinstance(kwargs['max'], int) or isinstance(kwargs['max'],float))):
                self.max = {'dft_value': kwargs['max']}

        elif 'df_physical' in kwargs:
            describe = kwargs['df_physical'].describe()
            self.max = {col:max(describe.loc['min',col], 
                                describe.loc['max',col]) for col in describe.columns}
            try:
                del self.max['date']
            except:
                pass
            print(self.max)
            self.set_conversion_matrix(**kwargs)
        else:
            raise ValueError("You must provide either describe, max, or df_physical.")
        
        

    def set_conversion_matrix(self, df_physical=None, df_standard=None, **kwargs):
        """
        Create a conversion dictionary between original values and standardized values.

        Parameters:
        - df (pd.DataFrame): The input DataFrame.
        - columns (list, optional): Columns to standardize. If None, all numeric columns are used.

        Returns:
        - dict: Conversion dictionary between original values and standardized values.
        """
        if df_physical is None and df_standard is None:
            raise ValueError("You must provide either df_physical or df_standard.")
        elif df_physical is None:
            df = df_standard
        elif df_standard is None:
            df = df_physical
        else:
            super(Max, self).set_conversion_matrix(df_physical, df_standard, **kwargs)
            return None

        # Get the optional arguments
        if 'columns' in kwargs:
            columns = kwargs['columns']
        else:
            columns = None

        # Initialise the optional arguments
        if columns is None:
            if 'dft_value' in self.max.keys():
                columns = df.columns
            else:
                columns = list(set(df.columns) & set(self.max.keys()))
                
        dict_out = {}
        if df_standard is None:
            for col in columns:
                if 'dft_value' in self.max.keys():
                    conversion = pd.DataFrame({'physical': df[col].to_numpy(),
                        'standard': (df[col] / self.max['dft_value']).to_numpy()})
                else:
                    conversion = pd.DataFrame({'physical': df[col].to_numpy(),
                                        'standard': (df[col] / self.max[col]).to_numpy()})
                conversion = conversion.drop_duplicates(subset=['physical'])
                dict_out[col] = conversion
        elif df_physical is None:
            for col in columns:
                if 'dft_value' in self.max.keys():
                    conversion = pd.DataFrame({'standard': df[col].to_numpy(),
                        'physical': (df[col] * self.max['dft_value']).to_numpy()})
                else:
                    conversion = pd.DataFrame({'standard': df[col].to_numpy(),
                        'physical': (df[col] / self.max[col]).to_numpy()})
                conversion = conversion.drop_duplicates(subset=['standard'])
                dict_out[col] = conversion
        self.conversion_matrix = dict_out
    
    def get_conversion_matrix(self, **kwargs):
        if self.conversion_matrix == None:
            self.set_conversion_matrix(**kwargs)
        return self.conversion_matrix
    
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
        
        # Get the optional arguments
        if 'columns' in kwargs:
            columns = kwargs['columns']
        else:
            columns = None

        # Initialise the optional arguments
        if columns is None:
            if 'dft_value' in self.max.keys():
                columns = df_physical.columns
            else:
                columns = list(set(df_physical.columns) & set(self.max.keys()))

        df_out = pd.DataFrame(index=df_physical.index,columns=columns)
        if 'dft_value' in self.max.keys():
            for col in columns:
                df_out[col] = df_physical[col] / self.max['dft_value']
        else:
            for col in columns:
                df_out[col] = df_physical[col] / self.max[col]
        return df_out
    
    def unstandardize (self, df_standard, **kwargs):
        """
        Unstandardize the columns of a DataFrame using mean and standard deviation.

        Parameters:
        - df (pd.DataFrame): The standardized DataFrame.
        - columns (list, optional): Columns to standardize. If None, all numeric columns are used.

        Returns:
        - pd.DataFrame: Unstandardized DataFrame.
        """
        
        # Get the optional arguments
        if 'columns' in kwargs:
            columns = kwargs['columns']
        else:
            columns = None

        # Initialise the optional arguments
        if columns is None:
            if 'dft_value' in self.max.keys():
                columns = df_standard.columns
            else:
                columns = list(set(df_standard.columns) & set(self.max.keys()))

        df_out = pd.DataFrame(index=df_standard.index,columns=columns)
        if 'dft_value' in self.max.keys():
            for col in columns:
                df_out[col] = df_standard[col] * self.max['dft_value']
        else:
            for col in columns:
                df_out[col] = df_standard[col] * self.max[col]
        return df_out

def load():
    """
    Load an instance of the MeanStd standardization class.

    Returns:
    - MeanStd: An instance of the MeanStd standardization class.
    """
    # Return an instance of the MSE class
    return Max()

