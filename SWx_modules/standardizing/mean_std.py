"""
mean_std.py - Mean Std standardization module.

This module defines a class MeanStd, which provides methods for computing the 
Mean Std standardization.
"""

import pandas as pd
from SWx_modules.standardizing.conversion import Conversion

class MeanStd(Conversion):
    """
    Mean Std standardization class.

    This class provides methods for computing the Mean Std standardization.
    """

    def __init__(self, **kwargs):
        """
        Initialize the MeanStd standardization instance.
        """
        super(MeanStd, self).__init__()
        try:
            self.set_attributes(**kwargs)
        except ValueError:
            self.mean = None
            self.std = None
    
    def set_attributes(self, **kwargs):
        """
        Set the attributes of the MeanStd standardization instance.
        """
        try: 
            super(MeanStd, self).set_attributes(**kwargs)
        except ValueError:
            self.conversion_matrix = None

        if 'describe' in kwargs:
            self.mean = dict(kwargs['describe'].loc['mean'])
            self.std = dict(kwargs['describe'].loc['std'])

        elif 'mean' in kwargs and 'std' in kwargs:
            if isinstance(kwargs['mean'], dict) and isinstance(kwargs['std'], dict):
                self.mean = kwargs['mean']
                self.std = kwargs['std']
            elif ((isinstance(kwargs['mean'], int) or isinstance(kwargs['mean'],float))
                  and isinstance(kwargs['std'], int) or isinstance(kwargs['std'],float)):
                self.mean = {'dft_value': kwargs['mean']}
                self.std = {'dft_value': kwargs['std']}

        elif 'df_physical' in kwargs:
            self.mean = dict(kwargs['df_physical'].describe().loc['mean'])
            self.std = dict(kwargs['df_physical'].describe().loc['std'])
            try:
                del self.mean['date']
            except:
                pass
            try:
                del self.std['date']
            except:
                pass
            self.set_conversion_matrix(**kwargs)
        else:
            raise ValueError("You must provide either describe, mean and std, or df.")
        print(self.mean, self.std)

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
            super(MeanStd, self).set_conversion_matrix(df_physical, df_standard, **kwargs)
            return None

        # Get the optional arguments
        if 'columns' in kwargs:
            columns = kwargs['columns']
        else:
            columns = None

        # Initialise the optional arguments
        if columns is None:
            if 'dft_value' in self.mean.keys():
                columns = df.columns
            else:
                columns = list(set(df.columns) & set(self.mean.keys()))
                
        dict_out = {}
        if df_standard is None:
            for col in columns:
                if 'dft_value' in self.mean.keys():
                    conversion = pd.DataFrame({'physical': df[col].to_numpy(), 
                        'standard': (df[col] - self.mean['dft_value']) / self.std['dft_value']})
                else:
                    conversion = pd.DataFrame({'physical': df[col].to_numpy(), 
                                        'standard': (df[col] - self.mean[col]) / self.std[col]})
                conversion = conversion.drop_duplicates(subset=['physical'])
                dict_out[col] = conversion
        elif df_physical is None:
            for col in columns:
                if 'dft_value' in self.mean.keys():
                    conversion = pd.DataFrame({'standard': df[col].to_numpy(),
                        'physical': (df[col] * self.std['dft_value'] + self.mean['dft_value']).to_numpy()})
                else:
                    conversion = pd.DataFrame({'standard': df[col].to_numpy(),
                        'physical': (df[col] * self.std[col] + self.mean[col]).to_numpy()})
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
            if 'dft_value' in self.mean.keys():
                columns = df_physical.columns
            else:
                columns = list(set(df_physical.columns) & set(self.mean.keys()))

        df_out = pd.DataFrame(index=df_physical.index,columns=columns)
        if 'dft_value' in self.mean.keys():
            for col in columns:
                df_out[col] = (df_physical[col] - self.mean['dft_value']) / self.std['dft_value']
        else:
            for col in columns:
                df_out[col] = (df_physical[col] - self.mean[col]) / self.std[col]
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
            if 'dft_value' in self.mean.keys():
                columns = df_standard.columns
            else:
                columns = list(set(df_standard.columns) & set(self.mean.keys()))

        df_out = pd.DataFrame(index=df_standard.index,columns=columns)
        if 'dft_value' in self.mean.keys():
            for col in columns:
                df_out[col] = df_standard[col] * self.std['dft_value'] + self.mean['dft_value']
        else:
            for col in columns:
                df_out[col] = df_standard[col] * self.std[col] + self.mean[col]
        return df_out

def load():
    """
    Load an instance of the MeanStd standardization class.

    Returns:
    - MeanStd: An instance of the MeanStd standardization class.
    """
    # Return an instance of the MSE class
    return MeanStd()

