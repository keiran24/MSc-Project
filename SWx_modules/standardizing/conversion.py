import pandas as pd

class Conversion():
    """
    Conversion class for converting between physical and standardized values.
    """
    def __init__(self, **kwargs):
        """
        Initialize the Conversion instance.
        """
        if 'conversion_matrix' in kwargs:
            self.conversion_matrix = kwargs['conversion_matrix']
        else:
            self.conversion_matrix = None
    
    def set_attributes(self, **kwargs):
        """
        Set the attributes of the Conversion instance.
        """
        if 'conversion_matrix' in kwargs:
            self.conversion_matrix = kwargs['conversion_matrix']
        elif 'df_physical' in kwargs and 'df_standard' in kwargs:
            self.set_conversion_matrix(kwargs['df_physical'], kwargs['df_standard'], **kwargs)
        else:
            raise ValueError("You must provide a conversion matrix or the Dataframes to build it.")

    def set_conversion_matrix(self, df_physical, df_standard, **kwargs):
        """
        Create an association dictionary between original values and ranked values.

        Parameters:
        - df_physical (pd.DataFrame): DataFrame with original values.
        - df_standard (pd.DataFrame): DataFrame with corresponding rank values.
        - columns (list, optional): Columns to create associations. If None, all columns are used.

        Returns:
        - dict: Association dictionary.
        """
        if 'columns' in kwargs:
            columns = kwargs['columns']
        else:
            columns = None

        dict_out = {}
        if columns is None:
            columns = df_standard.columns
        for col in columns:
            conversion = pd.DataFrame({'physical': df_physical[col].to_numpy(),
                                        'standard': df_standard[col].to_numpy()})
            conversion = conversion.drop_duplicates(subset=['standard'])
            dict_out[col] = conversion
        self.conversion_matrix = dict_out

    def get_conversion_matrix(self, **kwargs):
        if self.conversion_matrix == None:
            self.set_conversion_matrix(**kwargs)
        return self.conversion_matrix

    def standardize(self, df_physical,  **kwargs):
        """
        Replace physical values in a DataFrame with their corresponding standard values.

        Parameters:
        - df (pd.DataFrame): DataFrame with original values.
        - conversion_matrix (dict): Conversion dictionary.

        Returns:
        - pd.DataFrame: DataFrame with standard values.
        """
        if 'conversion_matrix' in kwargs:
            conversion_matrix = kwargs['conversion_matrix']
        else:
            conversion_matrix = self.conversion_matrix

        replacement_dict = {}
        for col in conversion_matrix.keys():
            if col in df_physical.columns:
                replacement_dict[col] = {conversion_matrix[col].at[i, 'physical']:
                                         conversion_matrix[col].at[i, 'standard']
                                    for i in conversion_matrix[col].index}
        return df_physical.replace(replacement_dict)

    def unstandardize(self, df_standard, **kwargs):
        """
        Replace standard values in a DataFrame with their corresponding physical values.

        Parameters:
        - df (pd.DataFrame): DataFrame with standard values.
        - conversion_matrix (dict): Conversion dictionary.

        Returns:
        - pd.DataFrame: DataFrame with physical values.
        """
        if 'conversion_matrix' in kwargs:
            conversion_matrix = kwargs['conversion_matrix']
        elif not self.conversion_matrix is None:
            conversion_matrix = self.conversion_matrix
        else:
            raise ValueError("You must provide a conversion matrix.")

        replacement_dict = {}
        for col in conversion_matrix.keys():
            if col in df_standard.columns:
                replacement_dict[col] = {conversion_matrix[col].at[i, 'standard']:
                                         conversion_matrix[col].at[i, 'physical']
                                    for i in conversion_matrix[col].index}
        return df_standard.replace(replacement_dict)

def load():
    """
    Load an instance of the MSE criteria class.

    Returns:
    - MSE: An instance of the MSE criteria class.
    """
    # Return an instance of the MSE class
    return Conversion()