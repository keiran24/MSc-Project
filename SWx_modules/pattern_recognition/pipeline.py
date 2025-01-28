"""
pipeline.py - Pipeline module for data processing and analog ensemble creation.

This module defines a class Pipeline, which represents a series of steps for loading data, splitting it, 
computing a criterion, listing analogs, and creating an ensemble of analogs.

Example Usage:
```python
filename = path_data + "omni_m_all_years.dat"
kwargs_loading = {columns:['year', 'doy', 'hour', 'earth_latitude', 'earth_longitude', 
    'BR_RTN', 'BT_RTN', 'BN_RTN', 'B', 'V_bulk', 'V_theta', 'V_phi', 'N_proton', 'T'],
                  fill_values:[np.nan, np.nan, np.nan, 9999.9, 9999.9, 999.9, 999.9, 
                  999.9, 999.9, 9999., 999.9, 999.9, 999.9, 9999999.]}
kwargs_splitting = {pattern_end:dt.datetime(year=2003,month=6,day=12,hour=0),
                     pattern_length:pd.to_timedelta(24,unit='h')}
criterion = 'mse'
kwargs_criterion = {columns:['V_bulk',]}
kwargs_analogs = {nb_analogs:1000, 
                  blind_window_length:pd.to_timedelta(24,unit='h'),
                  nb_extracted:10}
ensemble_MSEV_10 = Pipeline(filename=filename, kwargs_loading=kwargs_loading,
                    kwargs_splitting=kwargs_splitting, criterion=criterion,
                    kwargs_criterion=kwargs_criterion, kwargs_analogs=kwargs_analogs)   
"""

import pandas as pd
import numpy as np
import SWx_modules.file_management.filetodataframe as loading
import SWx_modules.pattern_recognition.splitting as splitting
from SWx_modules.pattern_recognition.criteria import CRITERIA
from SWx_modules.standardizing import STANDARDS
import SWx_modules.pattern_recognition.analog as analoglib
import SWx_modules.checking.keyindict as test_argument

class Pipeline():
    """
    Pipeline class for data processing and analog ensemble creation.

    Attributes:
    - data (pandas.DataFrame): The input data.
    - criterion (pandas.DataFrame): The computed criterion values.
    - analogs_index (pandas.Index or numpy.ndarray): The index of listed analogs.
    - ensemble_analogs (pandas.DataFrame or numpy.ndarray): The ensemble of extracted analogs.

    Methods:
    - set_data(**kwargs): Load data with specified loading parameters.
    - set_splitting(**kwargs): Split data into training, pattern, and forecast.
    - set_criterion(**kwargs): Compute the specified criterion on the training data.
    - set_analogs_index(**kwargs): List analogs based on the computed criterion.
    - set_ensemble_analogs(**kwargs): Extract the ensemble of analogs based on the listed analogs.
    """

    def __init__(self, standardizing=False, split=True, calcul_crit=True, list_analog=True, extract_analog=True, **kwargs):
        
        self.filename = test_argument.in_dic_or_default('filename', kwargs)
        self.data = test_argument.in_dic_or_default('data', kwargs)
        self.kwargs_loading = test_argument.in_dic_or_default('kwargs_loading', kwargs, default={})
        self.set_data(**self.kwargs_loading)

        self.kwargs_standard = test_argument.in_dic_or_default('kwargs_standard', kwargs, default={})
        self.kwargs_splitting = test_argument.in_dic_or_default('kwargs_splitting', kwargs, default={})
        self.kwargs_criterion = test_argument.in_dic_or_default('kwargs_criterion', kwargs, default={})
        self.kwargs_analogs = test_argument.in_dic_or_default('kwargs_analogs', kwargs, default={})

        if standardizing:
            self.set_standardizing(**self.kwargs_standard)

        if split:
            self.set_splitting(**self.kwargs_splitting)
            print('split = ok')
        if calcul_crit:
            self.set_criterion(**self.kwargs_criterion)
            print('criterion = ok')
        if list_analog:
            self.set_analogs_index(**self.kwargs_analogs)
            print('list_analog = ok')
        if extract_analog:
            self.set_ensemble_analogs(**self.kwargs_analogs)
        
    
    def set_data(self, **kwargs):
        if self.filename is None and self.data is None:
            raise ValueError('You must provide a filename or a dataframe.')
        elif self.filename is not None and self.data is not None:
            raise ValueError('You must provide a filename or a dataframe, not both.')
        elif self.filename is not None:
            self.kwargs_loading.update(kwargs)
            self.data = loading.file_to_time_series_dataframe(self.filename, **self.kwargs_loading)
        elif self.data is not None:
            if not isinstance(self.data, pd.DataFrame):
                raise TypeError('data must be a pandas.DataFrame.')
            if not isinstance(self.data.index, pd.DatetimeIndex):
                raise TypeError('data must have a DatetimeIndex.')
            
    def set_standardizing(self, **kwargs):
        if not hasattr(self, 'standard_name'):
            self.standard_name = test_argument.in_dic_or_valueerror('standard', kwargs, 
                                                                 error='You must provide a standard name.')
        if 'standard' in kwargs:    
            del kwargs['standard']
        if 'standard' in self.kwargs_standard:
            del self.kwargs_standard['standard']
        self.kwargs_standard.update(kwargs)
        self.original_data = self.data.copy()
        self.standard = STANDARDS[self.standard_name]
        self.standard.set_attributes(df_physical=self.original_data, **self.kwargs_standard)
        self.data = self.standard.standardize(self.data)
        

    def set_splitting(self, **kwargs):
        self.kwargs_splitting.update(kwargs)
        (self.data_train, self.data_pattern,
         self.data_forecast, counts) = splitting.split_data(self.data, **self.kwargs_splitting)
        self.kwargs_analogs.update({'size_analog':counts[0], 'size_forecast':counts[1]})

    def set_criterion(self, **kwargs):
        if not hasattr(self, 'criterion_name'):
            self.criterion_name = test_argument.in_dic_or_valueerror('criterion', kwargs, 
                                                                 error='You must provide a criterion name.')
        if 'criterion' in kwargs:    
            del kwargs['criterion']
        self.kwargs_criterion.update(kwargs)
        self.criterion = CRITERIA[self.criterion_name]
        frame = [self.criterion.moving_application(df, df_ref=self.data_pattern, **self.kwargs_criterion) 
                 for df in self.data_train]
        self.criterion = pd.concat(frame)
    
    def set_analogs_index(self, **kwargs):
        if not hasattr(self, 'criterion_name'):
            self.criterion_name = test_argument.in_dic_or_valueerror('criterion', kwargs, 
                                                                 error='You must provide a criterion name.')
        if 'criterion' in kwargs:     
            del kwargs['criterion']
        self.kwargs_analogs.update(kwargs)
        if isinstance(self.kwargs_analogs['blind_window_length'], list):
            custom_dtype = np.dtype([('blind_window_length', 'O'), ('analogs_index', 'O')])
            liste_analogs_index = []
            kwargs_analogs = self.kwargs_analogs.copy()
            for l in self.kwargs_analogs['blind_window_length']:
                kwargs_analogs.update({'blind_window_length':l})
                liste_analogs_index.append((l,analoglib.listing_analogs(self.criterion_name, self.criterion, **kwargs_analogs)))
            self.analogs_index = np.array(liste_analogs_index, dtype=custom_dtype)
        else:
            self.analogs_index = analoglib.listing_analogs(self.criterion_name, self.criterion, **self.kwargs_analogs)

    def set_ensemble_analogs(self, **kwargs): # Not compatible if multiple datasets
        self.kwargs_analogs.update(kwargs)

        if isinstance(self.kwargs_analogs['nb_extracted'], list) or isinstance(self.analogs_index, np.ndarray):
            custom_dtype = []
            if isinstance(self.analogs_index, np.ndarray):
                custom_dtype.append(*self.analogs_index.dtype.descr[:-1])
            if isinstance(self.kwargs_analogs['nb_extracted'], list):
                custom_dtype.append(('nb_extracted', 'int'))
                kwargs_analogs = self.kwargs_analogs.copy()
            custom_dtype.append(('ensemble_analogs', 'O'))
            custom_dtype = np.dtype(custom_dtype)

            liste_ensemble_analogs = []
            if isinstance(self.analogs_index, np.ndarray):
                for l, analog_index in self.analogs_index:
                    if isinstance(self.kwargs_analogs['nb_extracted'], list):
                        for n in self.kwargs_analogs['nb_extracted']:
                            kwargs_analogs.update({'nb_extracted':n})
                            liste_ensemble_analogs.append((l,n,analoglib.extract_analogs(self.data, analog_index, **kwargs_analogs)))
                    else:
                        liste_ensemble_analogs.append((l,analoglib.extract_analogs(self.data, analog_index, **kwargs_analogs)))
            else:
                for n in self.kwargs_analogs['nb_extracted']:
                    kwargs_analogs.update({'nb_extracted':n})
                    liste_ensemble_analogs.append((n,analoglib.extract_analogs(self.data, self.analogs_index, **kwargs_analogs)))
            self.ensemble_analogs = np.array(liste_ensemble_analogs, dtype=custom_dtype)

        else:
            self.ensemble_analogs = analoglib.extract_analogs(self.data, self.analogs_index, **self.kwargs_analogs)