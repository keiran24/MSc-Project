import json
import pandas as pd
import numpy as np
import warnings
from pandas._libs.tslibs import parsing
from SWx_modules.file_management.formats.abstract_format import Format

class JSON (Format):
    """
    Abstract class for file formats.
    """
    def __init__(self):
        super(JSON, self).__init__()
        self.extension = '.json'
        self.module = json
        self.binary = ''
    
    def save(self, obj, file_path, file_name, metadata=None, convert=True):
        if convert:
            obj = self.convert_to_jsoncompatible(obj)
        else:
            warnings.warn("Object not converted to JSON compatible format. This may cause errors when saving the file.")
        super(JSON,self).save(obj, file_path, file_name, metadata)
        
    def read(self, file_path, file_name, convert=True):
        data = super(JSON,self).read(file_path, file_name)
        if convert:
            return self.convert_from_jsoncompatible(data)
        return data

    def convert_to_jsoncompatible(self,obj,in_index=False):
        if isinstance(obj,np.ndarray): 
            return {'array':obj.tolist(),'dtype':str(obj.dtype)}
        elif isinstance(obj,list): 
            return [self.convert_to_jsoncompatible(item) for item in obj]
        elif isinstance(obj,dict): 
            return {'dict':{key:self.convert_to_jsoncompatible(obj[key]) for key in obj.keys()}}
        elif isinstance(obj,pd.DataFrame): 
            return {'dataframe':self.dataframe_to_jsondataframe(obj)}
        elif isinstance(obj,pd.Series): 
            return {'series':self.dataframe_to_jsondataframe(pd.DataFrame(obj))}
        elif 'Index' in str(type(obj)):
            return {'index':[self.convert_to_jsoncompatible(item,in_index=True) for item in obj],'dtype':str(type(obj[0]))}
        elif any(x in str(type(obj)) for x in ['time','Time','Date','date']) and in_index==False:
            return {'time':str(obj), 'dtype':str(type(obj))}
        elif any(x in str(type(obj)) for x in ['time','Time','Date','date']) and in_index==True:
            return str(obj)
        else: return obj
    
    def convert_from_jsoncompatible(self,obj):
        if isinstance(obj,list):
            return [self.convert_from_jsoncompatible(item) for item in obj]
        if isinstance(obj,dict):
            if 'dict' in obj:
                return {key:self.convert_from_jsoncompatible(obj['dict'][key]) for key in obj['dict'].keys()}
            if 'dataframe' in obj:
                return self.jsondataframe_to_dataframe(obj['dataframe'])
            if 'series' in obj:
                df = self.jsondataframe_to_dataframe(obj['series'])
                return df.iloc[:,0]
            if 'index' in obj and any(x in obj['dtype'] for x in ['time','Time','Date','date']):
                try: 
                    return pd.to_datetime(obj['index'])
                except parsing.DateParseError:
                    return pd.to_timedelta(obj['index'])
            elif 'index' in obj:
                return pd.Index(obj['index'],dtype=obj['dtype'])
            if 'array' in obj:
                return np.array(obj['array'],dtype=obj['dtype'])
            if 'time' in obj:
                try:
                    if ".date'" in obj['dtype']:
                        return pd.to_datetime(obj['time']).date()
                    else:
                        return pd.to_datetime(obj['time'])
                except parsing.DateParseError:
                    return pd.to_timedelta(obj['time'])
        return obj

    def dataframe_to_jsondataframe(self,df):
        out = {}
        df['index'] = df.index
        out['dtypes'] = dict(df.dtypes.astype(str))
        for col in df.columns:
            if df[col].dtype != int or df[col].dtype != float:
                df[col] = df[col].astype(str)
        out['dict'] = df.to_dict(orient='list')
        return out
    
    def jsondataframe_to_dataframe(self,json_dict):
        out = pd.DataFrame(json_dict['dict'])
        for col in out.columns:
            out[col] = out[col].astype(json_dict['dtypes'][col])
        out.index = out['index']
        out = out.drop(columns=['index'])
        return out

def load():
    """
    Load an instance of the JSON class.

    Returns:
    - An instance of the JSON class.
    """
    return JSON()

