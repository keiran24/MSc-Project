"""
__init__.py - Initialization module for the 'criteria' package.

This module provides functions for loading and managing criteria modules.

Functions:
- load_criterion(name):
    Load a criteria module by name.

- load_all():
    Load all available criteria modules.

Attributes:
- CRITERIA (dict): A dictionary mapping criteria names to their respective loaded modules.
"""

import importlib
import os

# Get the absolute path of the current directory
here = os.path.dirname(os.path.realpath(__file__))

def load_criterion(name):
    """
    Load a criteria module by name.

    Parameters:
    - name (str): The name of the criteria module to load.

    Returns:
    - object: The loaded criteria module.
    """
    # Import the specified criteria module dynamically
    mod = importlib.import_module(f"SWx_modules.pattern_recognition.criteria.{name}", "*")
    return mod.load()

def load_all():
    """
    Load all available criteria modules.

    Returns:
    - dict: A dictionary mapping criteria names to their respective loaded modules.
    """
    # List comprehension to get the names of all criteria modules
    criteria = [f[:-3] for f in os.listdir(here) if f[-3:] == '.py'
                and f != '__init__.py' and f != 'abstract_criterion.py']
    
    # Dictionary comprehension to load all criteria modules and create the mapping
    return {criterion: load_criterion(criterion) for criterion in criteria}

# Load all criteria modules and store them in the CRITERIA variable
CRITERIA = load_all()

