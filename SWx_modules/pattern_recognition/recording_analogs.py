import os
import time
from pathlib import Path
from SWx_modules.file_management.savloading import save, load
from SWx_modules.pattern_recognition.pipeline import Pipeline


def record_analogs(kwargs):
    start = time.time()
    print('Start:',kwargs['name'])
    # Make folder for recording if not existing
    path = kwargs['path_record']+kwargs['name']+'/'
    Path(path).mkdir(parents=True, exist_ok=True)

    # Params computation criterion and analogues
    name_object = 'params_pipeline_'
    extension = '.json'
    metadata = {'description':f"Parameters of the forecast of {kwargs['kwargs_criterion']['columns']} for pattern end date = {kwargs['date']} with pattern length {kwargs['length']}.",}
    pipeline = Pipeline(data=kwargs['df_quantity'], 
                        standardizing=False, split=True, calcul_crit=False, 
                        list_analog=False, extract_analog=False,
                        kwargs_loading=kwargs['kwargs_loading'],
                        kwargs_splitting=kwargs['kwargs_splitting'],
                        kwargs_criterion=kwargs['kwargs_criterion'],
                        kwargs_analogs=kwargs['kwargs_analogs'])
    del pipeline.kwargs_splitting['other_data']
    pipeline_to_record = {'data':{'quantity':kwargs['kwargs_criterion']['columns'],
                                'timestamp':[pipeline.data.index[0],pipeline.data.index[-1]]},
                         'data_forecast':[pipeline.data_forecast.index[0],pipeline.data_forecast.index[-1]],
                         'data_train':[[pipeline.data_train[idx].index[0],pipeline.data_train[idx].index[-1]] for idx in range(len(pipeline.data_train))],
                         'data_pattern':[pipeline.data_pattern.index[0],pipeline.data_pattern.index[-1]],
                         'kwargs_loading': pipeline.kwargs_loading,
                        'kwargs_splitting': pipeline.kwargs_splitting,
                        'kwargs_criterion': pipeline.kwargs_criterion,
                        'kwargs_analogs': pipeline.kwargs_analogs}

    if os.path.isfile(path+name_object+kwargs['name']+extension):
        print('Already recorded: '+path+name_object+kwargs['name']+extension+'.\n'
                      'File will be overwritten.')
    save(pipeline_to_record, 
         path, 
         name_object+kwargs['name']+extension, 
         extension[1:],
         metadata=metadata)
    print('Record: ',name_object+kwargs['name']+extension)

    # Computation criterion
    name_object = 'criterion_'
    extension = '.pkl'
    metadata = {'description':f"Criterion of the forecast of {kwargs['kwargs_criterion']['columns']} for pattern end date = {kwargs['date']} with pattern length {kwargs['length']}.",
                'params_path':path+name_object+kwargs['name']+extension}
    if os.path.isfile(path+name_object+kwargs['name']+extension):
        print('Using already recorded: ',path+name_object+kwargs['name']+extension)
        data = load(path, name_object+kwargs['name']+extension, extension[1:])
        pipeline.criterion = data['criterion']
        pipeline.criterion_name = data['criterion_name']
        pipeline.kwargs_criterion = data['kwargs_criterion']
    else:
        pipeline.set_criterion(**kwargs['kwargs_criterion'])
        criterion_to_record = {'criterion':pipeline.criterion,
                               'kwargs_criterion':pipeline.kwargs_criterion,
                               'criterion_name': pipeline.criterion_name,}
        if kwargs['save_crit']:
            save(criterion_to_record, 
                path, 
                name_object+kwargs['name']+extension, 
                extension[1:],
                metadata=metadata)
            print('Record: ',name_object+kwargs['name']+extension)

    # Computation analogues
    if len(kwargs['kwargs_criterion']['columns']) == 1:
        extension = '.json'
        name_object = 'analogues_'
        metadata = {'description':f"Analogues of the forecast of {kwargs['kwargs_criterion']['columns'][0]} for pattern end date = {kwargs['date']} with pattern length {kwargs['length']}.",
                    'params_path':kwargs['path_record']+kwargs['name']+'/params_pipeline_'+kwargs['name']+'.json',
                    'criterion_path':kwargs['path_record']+kwargs['name']+'/criterion_'+kwargs['name']+'.pkl'}
        if os.path.isfile(path+name_object+kwargs['name']+extension):
            print('Already recorded: ',path+name_object+kwargs['name']+extension)
        else: 
            kwargs['kwargs_analogs']['name_column'] = kwargs['kwargs_criterion']['columns'][0]
            pipeline.set_analogs_index(**kwargs['kwargs_analogs'])
            analogues_to_record = {'name_column':kwargs['kwargs_criterion']['columns'][0]}
            analogues_to_record['analogs_index'] = []
            for l,analogues in pipeline.analogs_index:
                analogues_to_record['analogs_index'].append({'blind_window_length':l,
                                                    'analogs_index':analogues})
            save(analogues_to_record, 
                    path, 
                    name_object+kwargs['name']+extension, 
                    extension[1:],
                    metadata=metadata)
        print('Record if not already recorded: ','analogues_'+'...'+extension)
    
    else:
        for quantity in kwargs['kwargs_criterion']['columns']:
            extension = '.json'
            name_object = 'analogues_'+quantity+'_'
            metadata = {'description':f"Analogues of the forecast of {quantity} for pattern end date = {kwargs['date']} with pattern length {kwargs['length']}.",
                        'params_path':kwargs['path_record']+kwargs['name']+'/params_pipeline_'+kwargs['name']+'.json',
                        'criterion_path':kwargs['path_record']+kwargs['name']+'/criterion_'+kwargs['name']+'.pkl'}
            if os.path.isfile(path+name_object+kwargs['name']+extension):
                print('Already recorded: ',path+name_object+kwargs['name']+extension)
            else: 
                kwargs['kwargs_analogs']['name_column'] = kwargs['kwargs_criterion']['columns'][0]
                pipeline.set_analogs_index(**kwargs['kwargs_analogs'])
                analogues_to_record = {'name_column':kwargs['kwargs_criterion']['columns'][0]}
                analogues_to_record['analogs_index'] = []
                for l,analogues in pipeline.analogs_index:
                    analogues_to_record['analogs_index'].append({'blind_window_length':l,
                                                        'analogs_index':analogues})
                save(analogues_to_record, 
                        path, 
                        name_object+kwargs['name']+extension, 
                        extension[1:],
                        metadata=metadata)
        print('Record if not already recorded: ','analogues_'+'...'+extension)
    
    print('End:',kwargs['name'], '(Time elapsed:', int(time.time() - start),'s)')
    return 0