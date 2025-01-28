from SWx_modules.file_management.formats import FORMATS
import os
import warnings
import pandas as pd

def save(obj, file_path, file_name, format_name=None, metadata=None):
    """
    Save an object to a file.

    Parameters:
    - obj (object): The object to be saved.
    - file_path (str): The path to the file.
    - file_name (str): The name of the file.
    - format_name (str): The name of the format module to use.
    - metadata (dict): Metadata to be saved with the object.
    """
    if format_name is None:
        format_name = file_name.split('.')[-1]
    assert format_name in FORMATS, f"Format {format_name} not found. Available formats: {list(FORMATS.keys())}."

    FORMATS[format_name].save(obj, file_path, file_name, metadata)

def load(file_path, file_name, format_name=None):
    """
    Load an object from a file.

    Parameters:
    - file_path (str): The path to the file.
    - file_name (str): The name of the file.
    - format_name (str): The name of the format module to use.

    Returns:
    - object: The object read from the file.
    """
    if format_name is None:
        format_name = file_name.split('.')[-1]
    assert format_name in FORMATS, f"Format {format_name} not found. Available formats: {list(FORMATS.keys())}."

    return FORMATS[format_name].read(file_path, file_name)

def load_metadata(file_path, file_name, format_name=None):
    """
    Load metadata from a file.

    Parameters:
    - file_path (str): The path to the file.
    - file_name (str): The name of the file.
    - format_name (str): The name of the format module to use.

    Returns:
    - dict: The metadata read from the file.
    """
    if format_name is None:
        format_name = file_name.split('.')[-1]
    assert format_name in FORMATS, f"Format {format_name} not found. Available formats: {list(FORMATS.keys())}."

    return FORMATS[format_name].read_metadata(file_path, file_name)

def load_folder(folder_path, name_files=None, format_names=None, df_concat=False):
    """
    Load all objects from files in a folder.

    Parameters:
    - folder_path (str): The path to the folder.
    - format_name (str): The name of the format module to use.

    Returns:
    - dict: A dictionary mapping file names to the objects read from the files.
    """
    if name_files is None:
        name_files = os.listdir(folder_path)

    if format_names is None:
        format_names = [name.split('.')[-1] for name in name_files]

    if isinstance(format_names, str):
        format_names = [format_names]*len(name_files)

    objects = []
    for name_file,format_name in zip(name_files,format_names):
        print('Loading file:', name_file)
        try:
            objects.append(load(folder_path, name_file, format_name))
        except AssertionError:
            print(f"Error loading file {name_file} Format {format_name} not found. Available formats: {list(FORMATS.keys())}.")

    if df_concat:
        check_df = sum([isinstance(obj, pd.DataFrame) for obj in objects])
        if check_df == len(objects):
            return pd.concat(objects, axis=0)
        else:
            warnings.warn("Not all objects are DataFrames. Returning list of objects.")
    
    return objects