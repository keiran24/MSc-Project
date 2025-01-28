"""
__init__.py - Initialization module for the 'format' package.

This module provides functions for loading and managing format modules.

Functions:
- load_format(name):
    Load a format module by name.

- load_all():
    Load all available format modules.

Attributes:
- FORMATS (dict): A dictionary mapping format names to their respective loaded modules.
"""

import importlib
import os

# Get the absolute path of the current directory
here = os.path.dirname(os.path.realpath(__file__))

def load_format(name):
    """
    Load a format module by name.

    Parameters:
    - name (str): The name of the format module to load.

    Returns:
    - object: The loaded format module.
    """
    # Import the specified criteria module dynamically
    mod = importlib.import_module(f"SWx_modules.file_management.formats.{name}", "*")
    return mod.load()

def load_all():
    """
    Load all available criteria modules.

    Returns:
    - dict: A dictionary mapping criteria names to their respective loaded modules.
    """
    # List comprehension to get the names of all criteria modules
    formats = [f[:-3] for f in os.listdir(here) if f[-3:] == '.py'
                and f != '__init__.py' and f != 'abstract_format.py']
    
    # Dictionary comprehension to load all criteria modules and create the mapping
    return {form: load_format(form) for form in formats}

# Load all criteria modules and store them in the CRITERIA variable
FORMATS = load_all()