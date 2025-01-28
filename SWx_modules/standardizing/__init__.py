"""
__init__.py - Initialization module for the 'standardizing' package.

This module provides functions for loading and managing standardizing modules.

Functions:
- load_standard(name):
    Load a standardizing module by name.

- load_all():
    Load all available standardizing modules.

Attributes:
- STANDARD (dict): A dictionary mapping standardizing names to their respective loaded modules.
"""

import importlib
import os

# Get the absolute path of the current directory
here = os.path.dirname(os.path.realpath(__file__))

def load_standard(name):
    """
    Load a standardizing module by name.

    Parameters:
    - name (str): The name of the standardizing module to load.

    Returns:
    - object: The loaded standardizing module.
    """
    # Import the specified criteria module dynamically
    mod = importlib.import_module(f"SWx_modules.standardizing.{name}", "*")
    return mod.load()

def load_all():
    """
    Load all available standardizing modules.

    Returns:
    - dict: A dictionary mapping standard names to their respective loaded modules.
    """
    # List comprehension to get the names of all criteria modules
    standards = [f[:-3] for f in os.listdir(here) if f[-3:] == '.py'
                and f != '__init__.py' and f != 'abstract_standard.py']
    
    # Dictionary comprehension to load all criteria modules and create the mapping
    return {standard: load_standard(standard) for standard in standards}

# Load all criteria modules and store them in the CRITERIA variable
STANDARDS = load_all()

