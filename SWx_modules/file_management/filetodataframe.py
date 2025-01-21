"""
loading.py

A module providing functions for common data-related tasks, including file downloading,
data loading into Pandas DataFrames, and time series index creation.

Functions:
- hdf5_to_dataframe(filename, h5_keys=[], df_columns={}, na_thresh={}):
    Load data from a HDF5 file into a Pandas DataFrame with customizable column names and
    replacement of invalid data.

- file_to_dataframe(filename, sep=None, columns=[], fill_values=[], header=None, 
               index_col=False, kwargs={}): 
    Load data from a file into a Pandas DataFrame with customizable options.
    
- set_time_serie_index(df, delete=True): 
    Convert a DataFrame with time-related columns to a time-series indexed DataFrame.

- file_to_time_series_dataframe(file_path, sep=None, columns=[], fill_values=[], header=None, 
                              index_col=False, kwargs={}, delete_time_cols=True):
    Load data from a file into a Pandas DataFrame with customizable options and format its 
    index as a time series.
    Use the loading_data and time_serie_index functions.

Examples:
>>> # Example of downloading a file
>>> download('https://example.com/data.csv', to='downloads/my_data.csv')

>>> # Example of loading data from a CSV file with custom settings
>>> file_path = 'example.csv'
>>> df = file_to_dataframe(file_path, sep=',', columns=['ID', 'Name', 'Age'], fill_values=['N/A', '-1'])

>>> # Example of creating a time series index from a DataFrame
>>> df_time_series = pd.DataFrame({'year': [2022, 2022, 2022],
...                                'month': [1, 2, 3],
...                                'day': [10, 15, 20],
...                                'hours': [8, 12, 16],
...                                'minutes': [30, 15, 45]})
>>> set_time_serie_index(df_time_series)
"""

import os
import pandas as pd
import h5py as h5
import numpy as np
import datetime

def hdf5_to_dataframe(filename, **kwargs):
    """
    Load data from a HDF5 file into a Pandas DataFrame with customizable column names 
    and replacement of invalid data.

    Parameters:
    - filename (str): The path to the HDF5 file.
    - kwargs (dict, optional): Other keyword arguments like 'h5_keys', 'df_columns', 'na_thresh'.
        - h5_keys (list): A list of keys to use from the HDF5 file.
        - df_columns (dict): A dictionary with key = h5_keys to rename the columns in the DataFrame.
        No need to include datetime columns. 
        - na_thresh (dict): A dictionary with key = df_columns with nan condition.
        Replace by nan np.abs(value) >= np.abs(na_thresh)

    Returns:
    - pandas.DataFrame: A DataFrame containing the data from the HDF5 file.

    Example:
    >>> df1 = hdf5_to_dataframe('example.h5')
    df1
    """

    # Assert that the file is in HDF5 format and exists
    assert filename.endswith('.h5'), "The file must be in HDF5 format."
    assert os.path.exists(filename), "The file does not exist."

    # List keys to use from the HDF5 file
    time_columns = [ 'time', 'datetime', 'date', 'dates', 'times', 'datetimes',
        'year', 'doy', 'month', 'day',
        'hours', 'hour', 'hr', 'h',
        'm', 'minute', 'min', 'minutes',
        'S', 'seconds', 'sec', 'second',
        'ms', 'milliseconds', 'millisecond', 'milli', 'millis',
        'us', 'microseconds', 'microsecond', 'micro', 'micros',
        'ns', 'nanoseconds', 'nano', 'nanos', 'nanosecond',]
    
    if 'h5_keys' in kwargs:
        columns = kwargs['h5_keys']
    else:
        with h5.File(filename, 'r') as f:
            columns = f.keys()

    # Load the file into a DataFrame using Pandas
    with h5.File(filename, 'r') as f:
        dic = {key: f[key][()] for key in f.keys() if key in columns or key in time_columns}
    df = pd.DataFrame(dic)

    # Custom column names
    if 'df_columns' in kwargs:
        df.rename(columns=kwargs['df_columns'], inplace=True)
    
    # Replace invalid data
    for k,key in enumerate(columns):
        if key in df.columns:
            mask = (np.abs(df[key]) >= np.abs(kwargs['na_thresh'][k]))
            df.loc[mask,key] = np.nan

    return df

def file_to_dataframe(filename, sep=None, columns=None, fill_values=None, **kwargs):
    """
    Load data from a file into a Pandas DataFrame with customizable options.
    Support file formats supported by pandas.read_csv.

    Parameters:
    - filename (str): The path to the file.
    - sep (str, optional): Delimiter to use. If None, the delimiter is set as whitespace.
    - columns (list or dict, optional): A list of column names to use for the DataFrame.
    If a dictionary is provided, the keys are the original hdf5 keys and the values are the new.
    - fill_values (list, optional): A list of values to be treated as NaN when reading the file.
    If a dictionary is provided, the keys are the column names and the values are the fill values.
    - kwargs (dict, optional): Other keyword arguments to pass to pandas.read_csv or hdf5_to_dataframe.

    Returns:
    - pandas.DataFrame: A DataFrame containing the data from the file.

    Example:
    >>> df1 = loading_data('example.csv')
    df1
    """

    # Manage file in HDF5 format
    if filename.endswith('.h5'):
        if isinstance(columns, dict) and not 'df_columns' in kwargs:
            kwargs['df_columns'] = columns
        if not 'na_thresh' in kwargs:
            if isinstance(fill_values,dict):
                kwargs['na_thresh'] = fill_values
            elif isinstance(fill_values, list) and isinstance(columns, list) and len(fill_values) == len(columns):
                kwargs['na_thresh'] = {col:val for col, val in zip(columns, fill_values)}
        return hdf5_to_dataframe(filename, **kwargs)
    
    # Manage file in other than HDF5 format
    else:
        if not 'sep' in kwargs:
            if sep is None:
                kwargs['delim_whitespace'] = True
            else:
                kwargs['sep'] = sep
        if not 'names' in kwargs and columns is not None and len(columns) > 0:
            kwargs['names'] = columns
        if not 'na_values' in kwargs and fill_values is not None and len(fill_values) > 0:
            kwargs['na_values'] = fill_values
        return pd.read_csv(filename, **kwargs)

def set_time_serie_index(df, delete=True):
    """
    Convert a DataFrame with time-related columns to a time-series indexed DataFrame.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing time-related columns.
    - delete (bool, optional): If True, delete the original time-related columns from the DataFrame.
                              Default is True.

    Returns:
    - pd.DataFrame: A time-series indexed DataFrame.

    The function interprets the time-related information in the DataFrame columns and creates a 
    time-series index.
    The time-related columns can include 'year', 'doy' (day of year), 'month', 'day', and various 
    time units like
    'hours', 'minutes', 'seconds', 'milliseconds', 'microseconds', 'nanoseconds', etc.

    If 'delete' is True, the original time-related columns are removed from the DataFrame.

    Raises:
    - ValueError: If the DataFrame does not contain the necessary date information.

    Example:
    >>> df = pd.DataFrame({'year': [2022, 2022, 2022],
    ...                    'month': [1, 2, 3],
    ...                    'day': [10, 15, 20],
    ...                    'hours': [8, 12, 16],
    ...                    'minutes': [30, 15, 45]})
    >>> time_serie_index(df)
    """
    
    columns_to_drop = []

    potential_datetime_columns = ['datetime', 'datetimes']
    datetime_columns = list(set(potential_datetime_columns).intersection(df.columns))
    if len(datetime) >= 1:
        # If 'datetime' is present, convert it to a datetime
        df.index = pd.to_datetime(df[datetime_columns[0]])
        columns_to_drop += datetime_columns
    
    else:
        # Convert date-related columns to a datetime
        dates_exist = True
        
        year = datetime.MINYEAR
        month = 1
        day = 1

        potential_date_columns = ['date', 'dates', 
                                  'year', 'years', 
                                  'month', 'months', 
                                  'day', 'days', 
                                  'doy', 'doys']
        
        date_columns = list(set(potential_date_columns[:2]).intersection(df.columns))
        year_columns = list(set(potential_date_columns[2:4]).intersection(df.columns))
        month_columns = list(set(potential_date_columns[4:6]).intersection(df.columns))
        day_columns = list(set(potential_date_columns[6:8]).intersection(df.columns))
        doy_columns = list(set(potential_date_columns[8:10]).intersection(df.columns))

        if len(date_columns)+len(year_columns)+len(month_columns)+len(day_columns)+len(doy_columns) == 0:
            dates_exist = False
        elif len(date_columns) >= 1:
            dates = pd.to_datetime(df[date_columns[0]])
        else:
            if len(year_columns) >= 1:
                year = df[year_columns[0]]
            if len(month_columns) >= 1:
                month = df[month_columns[0]]
            if len(day_columns) >= 1:
                day = df[day_columns[0]]
        
            if len(doy_columns) >= 1:
                dates = pd.to_datetime(year * 1000 + df[doy_columns], format='%Y%j')
            elif len(month_columns) == 0:
                dates = pd.to_datetime(year * 1000 + day, format='%Y%j')
            else:
                dates = pd.to_datetime(year * 1000 + month * 100 + day, format='%Y%m%d')

        if dates_exist and dates[0].year == datetime.MINYEAR:
            dates = dates - datetime.datetime(datetime.MINYEAR,1,1)

        columns_to_drop += date_columns + year_columns + month_columns + day_columns + doy_columns

        # Convert time-related columns to a timedelta and sum them up

        potential_time_columns = ['hours', 'hour', 'hr', 'h',
                              'm', 'minute', 'min', 'minutes',
                              'S', 'seconds', 'sec', 'second',
                              'ms', 'milliseconds', 'millisecond', 'milli', 'millis',
                              'us', 'microseconds', 'microsecond', 'micro', 'micros',
                              'ns', 'nanoseconds', 'nano', 'nanos', 'nanosecond']
        
        time_columns = list(set(potential_time_columns).intersection(df.columns))
        times = sum((pd.to_timedelta(df[col], unit=col)
                for col in time_columns), start=pd.to_timedelta(0))
        
        columns_to_drop += time_columns

        if dates_exist:
            df.index = dates + times
        else:
            df.index = times

    if delete:
        df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    return df

def file_to_time_series_dataframe(file_path, delete_time_cols=True, **kwargs):
    """
    Load data from a file into a Pandas DataFrame with customizable options and format its index 
    as a time series.

    Parameters:
    - file_path (str): The path to the file.
    - header (default=None, optional): Keyword arguments to pass to pandas.read_csv.
    - index_col (default=False, optional): Keyword arguments to pass to pandas.read_csv.
    - kwargs (dict, optional): Other keyword arguments to pass to pandas.read_csv.
    - delete_time_cols (bool, optional): If True, delete the original time-related columns from 
                                        the DataFrame. Default is True.

    Returns:
    - pandas.DataFrame: A time-series indexed DataFrame.
    """
    # Load data into a DataFrame using loading_data function
    df = file_to_dataframe(file_path, **kwargs)

    # Format the index as a time series using time_serie_index function
    df = set_time_serie_index(df, delete=delete_time_cols)

    return df
