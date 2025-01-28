"""
analog.py - Analog criteria module.

This module defines functions for listing analogs and extracting analogs from a DataFrame containing 
the value of the criterion variable.

Functions:
- listing_analogs(criterion, df_crit, name_column=None, nb_analogs=None, blind_window_length=None):
    List analogs based on a given criterion and DataFrame.

- extract_analogs(df, analogs_index, size_analog, size_forecast=None, nb_analogs=None, 
                    index_position=None):
    Extract analogs from a DataFrame based on the provided analog indexes.
"""

import numpy as np
import pandas as pd

from SWx_modules.pattern_recognition.criteria import CRITERIA
import SWx_modules.checking.keyindict as test_argument

def listing_analogs(criterion, df_crit, **kwargs):
    """
    List analogs based on a given criterion and DataFrame.

    Parameters:
    - criterion (str): The name of the criterion for sorting.
    - df_crit (pandas.DataFrame): The DataFrame containing the data for the criterion.
    - name_column (str, optional): The name of the column used for sorting.
    - nb_analogs (int, optional): The number of analogs to list.
    - blind_window_length (tuple or None, optional): Tuple specifying the blind window length.

    Returns:
    - pandas.Index: The index of listed analogs.
    """
    # Get the optional arguments
    name_column = test_argument.in_dic_or_default('name_column', kwargs, default=df_crit.columns[0])
    nb_analogs = test_argument.in_dic_or_default('nb_analogs', kwargs, default=len(df_crit))
    blind_window_length = test_argument.in_dic_or_default('blind_window_length', kwargs)
    # Set default values if not provided
    if not isinstance(blind_window_length, tuple):
        blind_window_length = (blind_window_length, blind_window_length)
    if not isinstance(blind_window_length[0], pd.Timedelta):
        if blind_window_length[0] is not None:
            raise TypeError('blind_window_length must be a tuple of pd.Timedelta. '
                            'Default value used.')
        return df_crit.nsmallest(nb_analogs,name_column).index

    # # Sort the DataFrame using the specified criterion
    # df_sorted = CRITERIA[criterion].sort(df_crit, name_column=name_column)
    # num_index = 0

    # # Iterate through the sorted DataFrame to list analogs
    # while num_index < nb_analogs and num_index < len(df_sorted):
    #     date = df_sorted.index[num_index]

    #     # Delete indexes within the blind window
    #     indexes_to_delete = df_crit.loc[date - blind_window_length[0]:date + blind_window_length[1]]
    #     indexes_to_delete = indexes_to_delete.drop(index=date).index
    #     df_sorted = df_sorted.drop(index=indexes_to_delete, errors='ignore')

    #     num_index += 1
    if isinstance(name_column, list):
        list_analogs = {}
        for col in name_column:
            list_analogs_col = []
            while len(list_analogs_col) < nb_analogs and len(df_crit)>0:
                list_analogs_col.append(df_crit[col].idxmin())
                df_crit = pd.concat([df_crit.loc[:list_analogs_col[-1] - blind_window_length[0]],
                                     df_crit.loc[list_analogs_col[-1] + blind_window_length[1]:]])
            list_analogs[col] = list_analogs_col
    else:
        list_analogs = []
        while len(list_analogs) < nb_analogs and len(df_crit)>0:
            list_analogs.append(df_crit.idxmin()[0])
            df_crit = pd.concat([df_crit.loc[:list_analogs[-1] - blind_window_length[0]],
                                    df_crit.loc[list_analogs[-1] + blind_window_length[1]:]])
    #return df_sorted.index[:num_index]
    return list_analogs

def extract_analogs(df, analogs_index, size_analog, **kwargs):
    """
    Extract analogs from a DataFrame based on the provided analog indexes.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the data.
    - analogs_index (pandas.Index): The index of analogs.
    - size_analog (int): The size of the analog window.
    - size_forecast (int, optional): The size of the forecast window.
    - nb_analogs (int, optional): The number of analogs to extract.
    - index_position (int, optional): The position within the analog window to locate the index.

    Returns:
    - pandas.DataFrame: The DataFrame with extracted analogs.
    """
    # Get the optional arguments
    size_forecast = test_argument.in_dic_or_default('size_forecast', kwargs, default=size_analog)
    nb_extracted = test_argument.in_dic_or_default('nb_extracted', kwargs,
                                                   default=len(analogs_index))
    index_position = test_argument.in_dic_or_default('index_position', kwargs,
                                                     default=-1) # end of the analog (pattern)

    if nb_extracted < len(analogs_index):
        analogs_index = analogs_index[:nb_extracted]

    df['date'] = df.index

    frames = []

    # Iterate through analog indexes to extract analogs
    for date in analogs_index:
        num_index = df.index.get_loc(date) - index_position
        df_analog = df.iloc[num_index - size_analog:num_index + size_forecast]
        df_analog.index = np.arange(0, len(df_analog), 1)
        frames.append(df_analog)

    # Concatenate the frames to create the output DataFrame
    df_out = pd.concat(frames, keys=analogs_index, names=['analog', 'index'])
    return df_out
