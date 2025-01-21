% matlab -nodisplay -nosplash -nodesktop -r "cd('/path/to/function/'); functionname(arg1, arg2);exit"
% Convert HDF4 files to HDF5 files
% path: path to the HDF4 files (e.g. '/path/to/')
% first_part_name: first part of the name of the HDF4 files (e.g. 'MAGSWE_data_64sec_')
% start_year: first year in name of the HDF4 files (e.g. 2000)
% end_year: last year in name of the HDF4 files (e.g. 2019)
% Example: hdf4tohdf5('/path/to/','MAGSWE_data_64sec_',2000,2019)

% Python script: 
% import matlab.engine
% eng = matlab.engine.start_matlab()
% eng.cd(path_library,nargout=0)
% eng.hdf4tohdf5('/path/to/','MAGSWE_data_64sec_',2000,2019,nargout=0)
% eng.quit() 

function hdf4tohdf5(path,first_part_name,start_year,end_year)
    extension = '.hdf';
    extension_out = '.h5';
    for year=start_year:end_year
        filename = [path first_part_name num2str(year)];
        filename_out = [filename extension_out];
        if isfile(filename_out)
            warning(sprintf('Warning: file does exist:\n%s', filename_out));
        else
            Dataset = hdfinfo([filename extension]).Vgroup.Vdata;
            Table = hdfread([filename extension],'MAGSWE_data_64sec');
            for i=1:size(Table,1)
                Name = Dataset.Fields(i).Name;
                Array = Table{i,1};
                h5create(filename_out,['/' Name],size(Array,2));
                h5write(filename_out,['/' Name],Array);
            end
        end
    end
end