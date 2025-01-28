"""
filtering.py

This module provides a function for resampling a time series DataFrame to a new resolution, 
allowing the specification of an aggregation function and the position of resampled timestamps.

Functions:
- time_filter(df, resolution, func=np.mean, index='center'):
    Resamples a time series DataFrame to a new resolution using a specified aggregation function 
    and index position.

Example Usage:
```python
import filtering

# Create a sample DataFrame with datetime index
df = ...

# Resample the DataFrame to a new resolution
result_df = filtering.time_filter(df, resolution='1D', func=np.sum, index='right')
"""

import pandas as pd
import numpy as np

def time_filter(df, resolution, **kwargs):
    """
    Resample a time series DataFrame to a new resolution using a specified aggregation function 
    and index position.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - resolution (str): The new resolution to resample the data.
    - func (callable, optional): The aggregation function to apply during resampling. 
      Default is np.mean.
    - index (str, optional): The position to place the resampled timestamps.
      Valid values: 'left', 'center' or 'right' 
      Default is 'center' and is used if an invalid value is given.

    Returns:
    - pd.DataFrame: The resampled DataFrame.
    """
    if 'func' in kwargs:
        func = kwargs['func']
    else:
        func = np.nanmean
    if 'index' in kwargs:
        index = kwargs['index']
    else:
        index = 'center'

    # Make a copy of the DataFrame to avoid modifying the original
    df_copy = df.copy()

    # Get the start time of the original data
    start = df_copy.index[0]

    # Calculate the original and new resolutions
    original_resolution = df_copy.index[1] - df_copy.index[0]
    new_resolution = pd.Timedelta(resolution)

    # Check if the new resolution is smaller than the original resolution
    if new_resolution < original_resolution:
        print(f'The resolution {resolution} is smaller than the time step of the data. '
              'Fill with NaNs.')

    # Resample the DataFrame to the new resolution using the specified aggregation function
    df_copy = df_copy.resample(resolution, origin=start).apply(func)

    # Adjust the index based on the specified position
    if new_resolution > original_resolution:
        if index == 'left':
            df_copy.index = df_copy.index
        elif index == 'right':
            df_copy.index = df_copy.index + new_resolution
        elif index == 'center':
            df_copy.index = df_copy.index + new_resolution / 2
        else:
            df_copy.index = df_copy.index + new_resolution / 2
            print(f'Invalid index position {index}. The default position "center" is used.')

    return df_copy

def time_window_filter(df, resolution, **kwargs):
    if 'func' in kwargs:
        func = kwargs['func']
    else:
        func = np.mean

    # Make a copy of the DataFrame to avoid modifying the original
    df_copy = df.copy()

    # Calculate the original and new resolutions
    original_resolution = df_copy.index[1] - df_copy.index[0]
    new_resolution = pd.Timedelta(resolution)

    # Check if the new resolution is smaller than the original resolution
    if new_resolution < original_resolution:
        print(f'The resolution {resolution} is smaller than the time step of the data. '
              'Fill with NaNs.')

    # Resample the DataFrame to the new resolution using the specified aggregation function
    df_copy = df_copy.rolling(resolution, center=True).apply(func)
    df_copy = df_copy.interpolate(method='nearest', limit_direction='both')

    return df_copy
