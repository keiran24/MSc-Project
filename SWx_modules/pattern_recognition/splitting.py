"""
splitting.py

The primary function is split_pattern_train_test, which splits a time series DataFrame into sets 
adapted to pattern recognition forecast.
The others functions are utility function to work with time series.

Functions:
- date_formatting(df, date, error=True):
    Format the date to ensure it is a valid datetime object.

- get_length_from_count(df, count):
    Calculate time length, count, and resolution based on a given count.

- get_length_from_dates(df, date_1, date_2):
    Calculate time length, count, and resolution based on two dates.

- get_length_from_portion(df, portion):
    Calculate time length, count, and resolution based on a portion of the DataFrame.

- get_length_from_time_length(df, time_length):
    Calculate count and resolution based on a given time length.

- get_length(df, date_start=None, date_end=None, portion=None, count=None, time_length=None, 
             error=False):
    Calculate time length, count, and resolution based on various input parameters.

- format_dates_for_splitting(df, pattern_start=None, pattern_end=None, test_start=None, 
                             test_end=None):
    Format the dates for the splitting function such as the pattern and test windows are 
    consecutives.

- get_counts_for_splitting(df, pattern_start=None, pattern_end=None, pattern_portion=None,
                            pattern_count=None, pattern_length=None,
                            test_start=None, test_end=None, test_portion=None,
                            test_count=None, test_length=None):
    Get the counts for the pattern and test sets based on the input parameters.

- split_data(df, pattern_start=None, pattern_end=None, pattern_portion=None,
                           pattern_count=None, pattern_length=None,
                           test_start=None, test_end=None, test_portion=None,
                           test_count=None, test_length=None):
    Split a time series DataFrame into pattern and test sets based on specified criteria.
    Depends on the resolution of the time series.

Example Usage:
```python
import splitting
import pandas as pd

# Create a sample DataFrame with datetime index
df = pd.DataFrame(index=pd.date_range('2022-01-01', '2022-12-31', freq='D'))

# Use the primary function
split_result = splitting.split_pattern_train_test(df, pattern_start='2022-01-01', 
                    pattern_length='30D', test_start='2022-02-01', test_length='15D')
"""

import datetime as dt
import pandas as pd

def date_formatting(df, date, error=True):
    """
    Format the date to ensure it is a valid datetime object.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - date (int, str, or datetime): The date to be formatted.
    - error (bool, optional): If True, raise a ValueError for invalid dates. Default is True.

    Returns:
    - datetime: The formatted date.

    Raises:
    - ValueError: If the date is not an integer, a string, or a datetime object.
    """
    if isinstance(date, int):
        date = df.index[date]
    elif isinstance(date, str):
        date = pd.to_datetime(date)
    elif not isinstance(date, dt.datetime):
        if error:
            raise TypeError('The date must be an integer, a string, or a datetime object.')
        else:
            return None
    return date

def get_length_from_count(df, count):
    """
    Calculate time length, count, and resolution based on a given count.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - count (int): The count used for calculations.

    Returns:
    - tuple: time_length, count, resolution.
    """
    resolution = df.index[1] - df.index[0]
    time_length = resolution * count
    return time_length, count, resolution

def get_length_from_dates(df, date_1, date_2):
    """
    Calculate time length, count, and resolution based on two dates (included).

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - date_1 (datetime): Start date.
    - date_2 (datetime): End date.

    Returns:
    - tuple: time_length, count, resolution.
    """
    count = len(df.loc[date_1:date_2].index)
    return get_length_from_count(df, count)

def get_length_from_portion(df, portion):
    """
    Calculate time length, count, and resolution based on a portion of the DataFrame.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - portion (float): The portion of the DataFrame.

    Returns:
    - tuple: time_length, count, resolution.
    """
    count = int(len(df.index) * portion)
    return get_length_from_count(df, count)

def get_length_from_time_length(df, time_length):
    """
    Calculate count and resolution based on a given time length.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - time_length (timedelta): The desired time length.

    Returns:
    - tuple: time_length, count, resolution.
    """
    count = int(time_length / (df.index[1] - df.index[0]))
    return get_length_from_count(df, count)

def get_length(df, **kwargs):
    """
    Calculate time length, count, and resolution based on various input parameters.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - date_start (int, str, or datetime, optional): Start date.
    - date_end (int, str, or datetime, optional): End date.
    - portion (float, optional): The portion of the DataFrame.
    - count (int, optional): The count used for calculations.
    - time_length (timedelta, optional): The desired time length.
    - error (bool, optional): If True, return None for invalid inputs. Default is False.

    Returns:
    - tuple: time_length, count, resolution.
    """

    if 'date_start' in kwargs:
        date_start = kwargs['date_start']
    else:
        date_start = None
    if 'date_end' in kwargs:
        date_end = kwargs['date_end']
    else:
        date_end = None

    if not (date_start is None or date_end is None) :
        date_start = date_formatting(df, date_start)
        date_end = date_formatting(df, date_end)
        if date_end < date_start:
            return get_length_from_dates(df, date_end, date_start)
        else:
            return get_length_from_dates(df, date_start, date_end)

    if 'count' in kwargs:
        count = kwargs['count']
    else:
        count = None

    if isinstance(count, int):
        return get_length_from_count(df, count)

    if 'time_length' in kwargs:
        time_length = kwargs['time_length']
    else:
        time_length = None

    if isinstance(time_length, dt.timedelta):
        return get_length_from_time_length(df, time_length)

    if 'portion' in kwargs:
        portion = kwargs['portion']
    else:
        portion = None

    if isinstance(portion, float):
        return get_length_from_portion(df, portion)

    if 'error' in kwargs:
        error = kwargs['error']
    else:
        error = False

    if error:
        return None, None, None
    else:
        return get_length_from_count(df, len(df.index))

def format_dates_for_splitting(df, **kwargs):
    """
    Format the dates for the splitting function such as the pattern and test windows are 
    consecutives.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - pattern_start (int, str, or datetime, optional): Start date for the pattern set.
    - pattern_end (int, str, or datetime, optional): End date for the pattern set.
    - test_start (int, str, or datetime, optional): Start date for the test set.
    - test_end (int, str, or datetime, optional): End date for the test set.

    Returns:
    - tuple: pattern_start, pattern_end, test_start, test_end
    """
    optional_arg = ['pattern_start', 'pattern_end',
                             'test_start', 'test_end',]
    for arg in optional_arg:
        if not arg in kwargs:
            kwargs[arg] = None

    pattern_start = date_formatting(df, kwargs['pattern_start'], error=False)
    pattern_end = date_formatting(df, kwargs['pattern_end'], error=False)
    test_start = date_formatting(df, kwargs['test_start'], error=False)
    test_end = date_formatting(df, kwargs['test_end'], error=False)

    # The pattern and test have to be consecutive
    if pattern_end is None:
        pattern_end = test_start - (df.index[1] - df.index[0])
    elif test_start is None:
        test_start = pattern_end + (df.index[1] - df.index[0])

    return pattern_start, pattern_end, test_start, test_end

def get_counts_for_splitting(df, **kwargs):
    """
    Get the counts for the pattern and test sets based on the input parameters.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - pattern_start (int, str, or datetime, optional): Start date for the pattern set.
    - pattern_end (int, str, or datetime, optional): End date for the pattern set.
    - pattern_portion (float, optional): The portion of the DataFrame for the pattern set.
    - pattern_count (int, optional): The count used for calculations for the pattern set.
    - pattern_length (timedelta, optional): The desired time length for the pattern set.
    - test_start (int, str, or datetime, optional): Start date for the test set.
    - test_end (int, str, or datetime, optional): End date for the test set.
    - test_portion (float, optional): The portion of the DataFrame for the test set.
    - test_count (int, optional): The count used for calculations for the test set.
    - test_length (timedelta, optional): The desired time length for the test set.

    Returns:
    - tuple: pattern_count, test_count, whole_count

    Notes:
    - Depends on the resolution of the time series.
    """
    optional_arg = ['pattern_start', 'pattern_end', 'pattern_portion',
                            'pattern_count', 'pattern_length',
                             'test_start', 'test_end', 'test_portion',
                             'test_count', 'test_length']
    for arg in optional_arg:
        if not arg in kwargs:
            kwargs[arg] = None

    _, whole_count, _ = get_length(df)
    _, pattern_count, _ = get_length(df,
                                     date_start=kwargs['pattern_start'],
                                     date_end=kwargs['pattern_end'],
                                     portion=kwargs['pattern_portion'],
                                     count=kwargs['pattern_count'],
                                     time_length=kwargs['pattern_length'],
                                     error=True)
    _, test_count, _ = get_length(df,
                                    date_start=kwargs['test_start'],
                                    date_end=kwargs['test_end'],
                                    portion=kwargs['test_portion'],
                                    count=kwargs['test_count'],
                                    time_length=kwargs['test_length'],
                                    error=True)

    if not isinstance(pattern_count,int) and not isinstance(test_count,int):
        raise ValueError('Not enough information to split the DataFrame.')
    elif not isinstance(pattern_count,int):
        pattern_count = test_count
    elif not isinstance(test_count,int):
        test_count = pattern_count

    return pattern_count, test_count, whole_count


def split_indexes(df, **kwargs):
    """
    Split a time series DataFrame into pattern and test sets based on specified criteria.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - pattern_start (int, str, or datetime, optional): Start date for the pattern set.
    - pattern_end (int, str, or datetime, optional): End date for the pattern set.
    - pattern_portion (float, optional): The portion of the DataFrame for the pattern set.
    - pattern_count (int, optional): The count used for calculations for the pattern set.
    - pattern_length (timedelta, optional): The desired time length for the pattern set.
    - test_start (int, str, or datetime, optional): Start date for the test set.
    - test_end (int, str, or datetime, optional): End date for the test set.
    - test_portion (float, optional): The portion of the DataFrame for the test set.
    - test_count (int, optional): The count used for calculations for the test set.
    - test_length (timedelta, optional): The desired time length for the test set.

    Returns:
    - list: [train_past_range, train_future_range], pattern_range, test_range, 
            [pattern_size, test_size].

    Notes:
    - Depends on the resolution of the time series.
    """
    pattern_start, pattern_end, test_start, test_end = format_dates_for_splitting(df, **kwargs)
    kwargs.update({'pattern_start':pattern_start, 'pattern_end':pattern_end,
                   'test_start':test_start, 'test_end':test_end})
    pattern_size, test_size, whole_count = get_counts_for_splitting(df, **kwargs)

    # Set the starting indexes
    test_start_index = 0 - test_size
    if  isinstance(test_start, dt.datetime):
        try:
            test_start_index = list(df.index).index(test_start)
        except:
            print("test_start not in index, considering the nearest previous date.")
            test_start_index = len(df.loc[:test_start].index)
    elif isinstance(pattern_start, dt.datetime):
        try:
            test_start_index = list(df.index).index(pattern_start) + pattern_size
        except:
            print("pattern_start not in index, considering the nearest previous date.")
            test_start_index = len(df.loc[:pattern_start].index) + pattern_size

    elif isinstance(test_end, dt.datetime):
        try:
            test_start_index = list(df.index).index(test_end) - test_size
        except:
            print("test_end not in index, considering the nearest previous date.")
            test_start_index = len(df.loc[:test_end].index) - test_size

    pattern_start_index = test_start_index - pattern_size
    if isinstance(pattern_start, dt.datetime):
        try:
            pattern_start_index = list(df.index).index(pattern_start)
        except:
            print("pattern_start not in index, considering the nearest previous date.")
            pattern_start_index = len(df.loc[:pattern_start].index)

    # Set the test and pattern sets
    pattern_indexes = df.iloc[pattern_start_index:pattern_start_index + pattern_size].index
    pattern_range = [pattern_indexes[0], pattern_indexes[-1]]
    test_indexes = df.iloc[test_start_index:test_start_index + test_size].index
    test_range = [test_indexes[0], test_indexes[-1]]

    # Set the training sets
    # Excluded from the training set: pattern, test, and last window of length test_size
    if pattern_start_index > pattern_size:
        train_past_indexes = df.iloc[:pattern_start_index].index
        train_past_range = [train_past_indexes[0], train_past_indexes[-1]]
    else:
        train_past_range = None
    if test_start_index + test_size + pattern_size < whole_count:
        train_future_indexes = df.iloc[test_start_index + test_size: 0 - test_size].index
        train_future_range = [train_future_indexes[0], train_future_indexes[-1]]
    else:
        train_future_range = None

    return ([train_past_range, train_future_range], pattern_range, test_range,
            [pattern_size, test_size])

def split_data(df, **kwargs):
    """
    Split a time series DataFrame into pattern and test sets based on specified criteria.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with a datetime index.
    - pattern_start (int, str, or datetime, optional): Start date for the pattern set.
    - pattern_end (int, str, or datetime, optional): End date for the pattern set.
    - pattern_portion (float, optional): The portion of the DataFrame for the pattern set.
    - pattern_count (int, optional): The count used for calculations for the pattern set.
    - pattern_length (timedelta, optional): The desired time length for the pattern set.
    - test_start (int, str, or datetime, optional): Start date for the test set.
    - test_end (int, str, or datetime, optional): End date for the test set.
    - test_portion (float, optional): The portion of the DataFrame for the test set.
    - test_count (int, optional): The count used for calculations for the test set.
    - test_length (timedelta, optional): The desired time length for the test set.

    Returns:
    - list: [data_train_past, data_train_future], data_pattern, data_test, 
            [pattern_size, test_size].

    Notes:
    - Depends on the resolution of the time series.
    """
    if 'other_data' in kwargs:
        other_data = kwargs['other_data']
    else:
        other_data = []

    range_train, range_pattern, range_test, counts = split_indexes(df, **kwargs)

    data_test = df.loc[range_test[0]:range_test[1]]
    data_pattern = df.loc[range_pattern[0]:range_pattern[1]]
    data_train_past = df.loc[range_train[0][0]:range_train[0][1]]
    data_train_future = df.loc[range_train[1][0]:range_train[1][1]]

    return [data_train_past, data_train_future,]+other_data, data_pattern, data_test, counts
