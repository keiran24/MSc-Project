#%%
import sys
import pandas as pd
from itertools import product
import time
from pathlib import Path
from multiprocessing import Pool


sys.path.append('C:/Users/pauline/OneDrive - Queen Mary, University of London/REPO_POSTDOC_2023_2025/Space_Weather_Project/scripts/pattern_recognition_forecast/Article/')
import params
from SWx_modules.file_management.savloading import load
from SWx_modules.pattern_recognition.recording_analogs import record_analogs

if __name__ == "__main__":

    #%%
    Path(params.path_forecast).mkdir(parents=True, exist_ok=True)

    df_quantity = load(params.path_dataset, params.file_dataset, params.file_dataset.split('.')[-1])
    other_datasets = [load(params.path_dataset, file, file.split('.')[-1]) for file in params.other_files]
    quantities = params.quantities
    lengths = params.pattern_size
    resolution = params.resolution
    pattern_ends = load(params.path_pattern_ends,params.file_pattern_ends, params.file_pattern_ends.split('.')[-1])
    quantity_length_date = [*product(quantities,lengths,pattern_ends)]

    #%%
    kwargs = ({'date':date,
                'length':length,
                'df_quantity':df_quantity[[quantity]],
                'path_record': params.path_forecast+'/'+quantity+'/',
                'kwargs_loading': params.kwargs_dataset,
                'kwargs_splitting':{'pattern_length':pd.to_timedelta(resolution)*length,
                                    'pattern_end':date,
                                    'other_data':[other_datasets[o][[quantity]] for o in range(len(other_datasets))]},
                'kwargs_criterion': {**params.kwargs_criterion,'columns':[quantity,],},
                'kwargs_analogs': params.kwargs_analogs,
                'save_crit':False,
                'name':quantity+'_LP'+str(length)+'_'+str(date).replace('-','').replace(' ','').replace(':','').replace('.','')} 
                for quantity,length,date in quantity_length_date)

    #%%
    with Pool(8) as p:
        start = time.time()
        for x in p.imap_unordered(record_analogs, kwargs):
            print("{} (Time elapsed: {}s)".format(x, int(time.time() - start)))

