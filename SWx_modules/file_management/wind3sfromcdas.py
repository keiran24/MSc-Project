""" Module to download Wind/MFI and 3DP 3s-resolution data from CDAS.
    The data is saved in json files in the specified path.
    The data is saved as a dictionary with the following structure:
    {'metadata': {'date': '2021-06-01 12:00:00',
                    'git_commit': 'a1b2c3d4e5f6g7h8i9j0',
                    'git_dir': '/path/to/git/repo',
                    'description': ...},
    'data': {'dataframe': {'dtypes': {'column1': 'float64', 'column2': 'int64',
                                     ...,
                                     'index': 'datetime64[ns]'},
                            'dict': {'column1': [value1, value2, ...],
                                    'column2': [value1, value2, ...],
                                    ...,
                                    'index': [index1, index2, ...]}}},
    The data can be read with the function read_from_json from the same module.

"""

import os
from pathlib import Path
import datetime
import pandas as pd
import numpy as np
from cdasws import CdasWs

import SWx_modules.file_management.savloading as sl

cdas = CdasWs()


def download_mag_rtn_3s(start, end):
    """Download Wind MFI (magnetic field) in RTN coordinate system and with 3s resolution.
    start, end format:  '2005-01-01' or datetime.datetime"""
    dataset = 'WI_H3-RTN_MFI'
    var_names = list(set(cdas.get_variable_names(dataset)) & set(['B3RTN','B3F1']))
    _, data = cdas.get_data(dataset, var_names, start, time1=end)
    data_output = pd.DataFrame(index=data['Epoch3'])
    data_output['Br_rtn'] = data['B3RTN'][:,0]
    data_output['Bt_rtn'] = data['B3RTN'][:,1]
    data_output['Bn_rtn'] = data['B3RTN'][:,2]
    data_output['B'] = data['B3F1']
    return data_output

def download_mag_gse_3s(start, end):
    """Download Wind MFI (magnetic field) in GSE coordinate system and with 3s resolution.
    start, end format:  '2005-01-01' or datetime.datetime"""
    dataset = 'WI_H0_MFI'
    var_names = list(set(cdas.get_variable_names(dataset)) & set(['B3GSE','B3F1']))
    _, data = cdas.get_data(dataset, var_names, start, time1=end)
    data_output = pd.DataFrame(index=data['Epoch3'])
    data_output['Bx_gse'] = data['B3GSE'][:,0]
    data_output['By_gse'] = data['B3GSE'][:,1]
    data_output['Bz_gse'] = data['B3GSE'][:,2]
    data_output['B'] = data['B3F1']
    return data_output

def download_mag_gsm_3s(start, end):
    """Download Wind MFI (magnetic field) in GSM coordinate system and with 3s resolution.
    start, end format:  '2005-01-01' or datetime.datetime"""
    dataset = 'WI_H0_MFI'
    var_names = list(set(cdas.get_variable_names(dataset)) & set(['B3GSM','B3F1']))
    _, data = cdas.get_data(dataset, var_names, start, time1=end)
    data_output = pd.DataFrame(index=data['Epoch3'])
    data_output['Bx_gsm'] = data['B3GSM'][:,0]
    data_output['By_gsm'] = data['B3GSM'][:,1]
    data_output['Bz_gsm'] = data['B3GSM'][:,2]
    data_output['B'] = data['B3F1']
    return data_output

def download_pm_3s(start, end):
    """Download Wind 3dp proton moments with 3s resolution.
    start, end format:  '2005-01-01' or datetime.datetime"""
    dataset = 'WI_PM_3DP'
    var_names = list(set(cdas.get_variable_names(dataset))
                    & set(['P_VELS','P_DENS','P_TEMP','VALID']))
    _, data = cdas.get_data(dataset, var_names, start, time1=end)
    data_output = pd.DataFrame(index=data['Epoch'])
    data_output['Vx_gse'] = data['P_VELS'][:,0]
    data_output['Vy_gse'] = data['P_VELS'][:,1]
    data_output['Vz_gse'] = data['P_VELS'][:,2]
    data_output['Np'] = data['P_DENS']
    data_output['Tp'] = data['P_TEMP']
    data_output['valid'] = data['VALID']
    return data_output

def download_swe_3s(start, end):
    """Download Wind 3dp proton moments with 3s resolution.
    start, end format:  '2005-01-01' or datetime.datetime"""
    dataset = 'WI_H1_SWE'
    var_names = list(set(cdas.get_variable_names(dataset))
                    & set(['P_VELS','P_DENS','P_TEMP','VALID']))
    _, data = cdas.get_data(dataset, var_names, start, time1=end)
    data_output = pd.DataFrame(index=data['Epoch'])
    data_output['Vx_gse'] = data['P_VELS'][:,0]
    data_output['Vy_gse'] = data['P_VELS'][:,1]
    data_output['Vz_gse'] = data['P_VELS'][:,2]
    data_output['Np'] = data['P_DENS']
    data_output['Tp'] = data['P_TEMP']
    data_output['valid'] = data['VALID']
    return data_output

class Wind3sFromCdas:
    """ Class to download Wind/MFI and 3DP 3s-resolution data from CDAS."""
    def __init__(self,path_data,years,dict_params=None):

        assert isinstance(path_data, str), 'path_data must be a string.'
        Path(path_data).mkdir(exist_ok=True)
        self.path_data = path_data

        assert isinstance(years, list), 'years must be a list of years.'
        assert len(years) > 0, 'years must contain at least one year.'
        self.years_to_download = years

        if dict_params is None:
            dict_params = {'type': ['pm','mag_gse','mag_gsm','mag_rtn']}
        assert isinstance(dict_params,dict), 'dict_params must be a dictionary.'
        assert 'type' in dict_params, 'dict_params must contain the key "type".'
        assert isinstance(dict_params['type'],list), 'dict_params["type"] must be a list.'

        self.pm = 'pm' in dict_params['type']
        self.mag_gse = 'mag_gse' in dict_params['type']
        self.mag_gsm = 'mag_gsm' in dict_params['type']
        self.mag_rtn = 'mag_rtn' in dict_params['type']
        self.mag = self.mag_gse or self.mag_gsm or self.mag_rtn

        if 'particule' in dict_params:
            self.particule = dict_params['particule']
        else:
            self.particule = ('pm'*self.pm
                                + '-'*self.pm*self.mag
                                + 'mag'*self.mag
                                + '-gse'*self.mag_gse
                                + '-gsm'*self.mag_gsm
                                + '-rtn'*self.mag_rtn)

        self.name_suffix = "wind_"+self.particule+'_3s_'

        if 'extension' in dict_params:
            self.extension = dict_params['extension']
        else:
            self.extension = '.json'

        self.name_files = {year: None for year in self.years_to_download}
        self.check_files_already_in_path_data()

        print('Years to download: ',self.years_to_download)
        print('Quantities to download: ',self.particule)
        print('Record path: ',self.path_data)
        print('Use method "scdata_from_cdas" to download the data.')

    def check_files_already_in_path_data(self):
        """ verif if file already in folder """
        files = os.listdir(self.path_data)
        files = {int(f[len(self.name_suffix):len(self.name_suffix)+4]): f
                 for f in files if f.startswith(self.name_suffix) and f.endswith(self.extension)}
        years = []
        for year in self.years_to_download:
            if year in files:
                print('File ',files[year],' already exist.')
                self.name_files[year] = files[year]
            else:
                years.append(year)
        self.years_to_download = years

    def missing_values_to_nan_inplace(self,pm=None, mag=None):
        """Replace missing/invalid values in the WIND/MFI and WIND/3dp with NaN."""
        try:
            if min(mag['B']) < -1e28:
                mag.replace(min(mag['B']),np.nan,inplace=True)
        except (TypeError,KeyError, AttributeError):
            pass
        try:
            pm.where(pm['valid']==1,inplace=True)
            del pm['valid']
        except (TypeError, KeyError, AttributeError):
            pass

    def join_mag(self, mag_gse=None, mag_rtn=None, mag_gsm=None):
        """ Try to join the magnetic field data from GSE, GSM and 
        RTN coordinate systems in a single DataFrame."""
        mag = pd.DataFrame()
        exception = 0
        try:
            for k in mag_gse:
                mag[k] = mag_gse[k]
        except (KeyError, AttributeError,TypeError):
            exception += 1
        try:
            for k in mag_gsm:
                mag[k] = mag_gsm[k]
        except (KeyError, AttributeError,TypeError):
            exception += 1
        try:
            for k in mag_rtn:
                mag[k] = mag_rtn[k]
        except (KeyError, AttributeError,TypeError):
            exception += 1
        if exception == 3:
            return None
        return mag

    def join_pm_mag(self,pm=None,mag=None):
        """ Try to join the proton moments and magnetic field 
        data in a single DataFrame."""
        try:
            pm_mag = pd.concat([pm,mag]).sort_index(axis=0)
        except (ValueError,TypeError):
            pm_mag = None
        return pm_mag

    def time_regul(self,df=None):
        """ Regularize the time of the DataFrame to 3s resolution."""
        try:
            df = df.resample('3s').mean(numeric_only=True).shift(periods=1,freq='s')
        except AttributeError:
            df = None
        return df

    def naming_record_file(self,time0='',time1=''):
        """ Set the name of the record file with the particule and the time."""
        output = self.name_suffix
        output += str(time0).replace('-','').replace(' ','').replace(':','').replace('.','')
        output += '_'
        output += str(time1).replace('-','').replace(' ','').replace(':','').replace('.','')
        output += self.extension
        return output

    def pretty_save_as_json(self,data):
        """ Convert the DataFrame to a json-compatible dictionary. Return also a description"""
        metadata = {'description': f'Wind {self.particule} 3s data from CDAS.'
                    f'Download through custom module.'}
        return metadata

    def scdata_from_cdas(self):
        """ Download Wind/MFI and 3DP 3s-resolution data from CDAS 
        for the years in the list 'years'. """

        time0_list = [datetime.datetime(year=year,month=1,day=1,hour=0,tzinfo=datetime.timezone.utc) 
                 for year in self.years_to_download]
        time1_list = [datetime.datetime(year=year+1,month=1,day=1,hour=0,tzinfo=datetime.timezone.utc)
                    for year in self.years_to_download]
        
        for year,time0,time1 in zip(self.years_to_download,time0_list,time1_list):

            data_mag_gse = None
            if self.mag_gse:
                data_mag_gse = download_mag_gse_3s(time0,time1)
                print('Downloaded GSE magnetic field data for year',year)
            data_mag_gsm = None
            if self.mag_gsm:
                data_mag_gsm = download_mag_gsm_3s(time0,time1)
                print('Downloaded GSM magnetic field data for year',year)
            data_mag_rtn = None
            if self.mag_rtn:
                data_mag_rtn = download_mag_rtn_3s(time0,time1)
                print('Downloaded RTN magnetic field data for year',year)
            data_mag = self.join_mag(mag_gse=data_mag_gse,mag_gsm=data_mag_gsm,mag_rtn=data_mag_rtn)
            del(data_mag_gse,data_mag_gsm,data_mag_rtn)
            self.missing_values_to_nan_inplace(mag=data_mag)

            data_pm = None
            if self.pm:
                data_pm = download_pm_3s(time0,time1)
                print('Downloaded proton moments data for year',year)
                self.missing_values_to_nan_inplace(pm=data_pm)
                data = self.join_pm_mag(pm=data_pm,mag=data_mag)
                data = self.time_regul(df=data)
            else:
                data = data_mag
            
            try:
                assert data is not None, f'No data to record for year {year}.'
            except AssertionError as e:
                print(e)
                continue
            
            name_record_file = self.naming_record_file(time0=data.index[0],time1=data.index[-1])
            metadata = {'description': f'Wind {self.particule} 3s data from CDAS.'
                    f'Download through custom module.'}
            sl.save(data,self.path_data,name_record_file,format_name=self.extension[1:],metadata=metadata)
            print('Recorded data for year',year,'in file',name_record_file)
            self.name_files[year] = name_record_file
            
