"""
loading.py

A module providing functions for file downloading.

Functions:
- download(url, to=None): 
    Download a file from a URL and save it to a specified destination.

Examples:
>>> # Example of downloading a file
>>> download('https://example.com/data.csv', to='downloads/my_data.csv')
'downloads/my_data.csv'
"""

import os
import warnings
from urllib.request import urlretrieve
from SWx_modules.file_management.savloading import save

def download_from_url(url, to=None, metadata=True):
    """
    Download a file from a given URL and save it to a specified destination.

    Parameters:
    - url (str): The URL from which to download the file.
    - to (str, optional): The optional destination path where the file should be saved.
      If None, the base name of the URL is used as filename and the file saved in the current directory.

    Returns:
    - str: The path where the file is saved or already exists.

    If 'to' is None, it is set to the base name of the URL and will be saved in the current 
    directory.
    The function checks whether a file already exists at the specified destination ('to'). 
    If it does not exist, the function uses 'urlretrieve' from 'urllib.request' to download the file 
    from the given URL and save it to the specified location. If the file already exists, 
    a message is printed indicating that the file is already present.

    Example:
    >>> download('https://example.com/file.txt', to='downloads/myfile.txt')
    'downloads/myfile.txt'
    """

    # If 'to' is not provided, set it to the base name of the URL
    if to is None:
        to = os.path.basename(url)
    
    # Check if the file already exists at the specified destination ('to')
    assert not os.path.exists(to), f"File {to} already exists."

    if metadata == False:
        warnings.warn('Metadata will not be saved with the file.', UserWarning)
    else:
        metadata = {'description': 'Downloaded file from URL'}
        path = to[:-len(to.split('/')[-1])]
        name = 'log_'+to.split('/')[-1][:-len(to.split('.')[-1])-1]
        save({'file': to, 'url': url}, path, name, format_name='json', metadata=metadata)

    # Download the file from the URL and save it to the specified location
    urlretrieve(url, to)

    # Return the path where the file is saved or already exists
    return to