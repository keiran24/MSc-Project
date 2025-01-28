#%% Modules
from SWx_modules.file_management.savloading import load

#%% Paths
## Path to the current repository and the associated data
path_repo = 'C:/Users/pauline/OneDrive - Queen Mary, University of London/REPO_POSTDOC_2023_2025/Space_Weather_Project/'
path_data_repo = 'C:/Users/pauline/Documents/DATA/Space_Weather_Project/'
path_data = path_data_repo + 'pattern_recognition_forecast/Article/'
path_local_folder = path_repo + 'scripts/pattern_recognition_forecast/Article/'

## Path to save
path_pictures = path_local_folder + 'results/'

#%% Params dataset
## Path to the dataset
path_dataset = path_data + 'Datasets/'
file_dataset = 'wind_plsp_24s_20040503000024_20061121235912.pkl'
other_files = ['wind_plsp_24s_20071001000024_20080430230512.pkl',
                'wind_plsp_24s_20080601000048_20090831000024.pkl']
quantities = ['Proton_VX_GSE','Proton_VY_GSE','Proton_VZ_GSE'] #'B','BX_GSE','BY_GSE','BZ_GSE','Proton_V',
kwargs_dataset = {'path':path_dataset, 'name':file_dataset}

#%% Params dates
## Path to the list of dates
path_dates = path_dataset
file_dates = 'dates_5pctnans_4pctgaps_200.json'

#%% Params forecast
## Path to the forecast results
### Path = path_forecast / path_forecast_folder / suffixe_ LPNumUnit_date / file_ suffixe_ LPnum_date . ext
path_forecast = path_data + 'Forecast_RMSE/'
path_forecast_folder = ''
suffixe = ''
file_params = 'params_pipeline_'
file_analogues = 'analogues_'
ext = '.json'

## Params splitting
### Values to add in kwargs: 'pattern_length' as (Num,Unit) and 'pattern_end' as datetime
pattern_size = load(path_dataset, 'pattern_size_10.json', 'json')['pattern_size']
resolution = load(path_dataset, 'pattern_size_10.json', 'json')['resolution']
path_pattern_ends = path_dataset
file_pattern_ends = file_dates
kwargs_splitting = {'pattern_length':None, 'pattern_end':None, 'other_datasets':None}

## Params compute criterion
### Values to add in kwargs: 'columns' as ['',]
nanprop = 10
criterion = 'mse'
kwargs_criterion = {'criterion':'mse', 'nanprop':nanprop, 'columns':None}

## Params selection analogues
nb_analogs = 500
blind_window_length = [None,]
nb_extracted = []
kwargs_analogs = {'nb_analogs':nb_analogs,
                  'blind_window_length':blind_window_length,
                  'nb_extracted':nb_extracted,}

## Params for perf
full_dataset_file = 'wind_plsp_24s_20040503000000_20090831000024.pkl'
forecast_length = '1000h'
path_performances = path_data + 'Performances/'