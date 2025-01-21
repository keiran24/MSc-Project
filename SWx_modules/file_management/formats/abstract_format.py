import git
import datetime

class Format:
    """
    Abstract class for file formatings.
    """
    def __init__(self):
        self.extension = ''
        self.module = None
        self.binary = ''
    
    def get_metadata(self,metadata=None):
        if isinstance(metadata, dict):
            metadata = metadata
        else:
            metadata = {}
        metadata['date'] = str(datetime.datetime.now())
        repo = git.Repo(search_parent_directories=True)
        metadata['git_commit'] = repo.head.commit.hexsha
        metadata['git_dir'] = repo.working_dir
        return metadata

    def save(self, obj, file_path, file_name, metadata=None):
        """
        Save an object to a file.

        Parameters:
        - obj (object): The object to be saved.
        - file_path (str): The path to the file.
        - file_name (str): The name of the file.
        - metadata (dict): Metadata to be saved with the object.
        """
        dict_to_save = {'metadata': self.get_metadata(metadata),
                        'data': obj}
        name = file_path + file_name
        if not name.endswith(self.extension):
            name += self.extension
        with open(name, 'w'+self.binary) as f:
            self.module.dump(dict_to_save, f)
        

    def read(self, file_path, file_name):
        """
        Read an object from a file.

        Parameters:
        - file_path (str): The path to the file.
        - file_name (str): The name of the file.

        Returns:
        - object: The object read from the file.
        """
        name = file_path + file_name
        if not name.endswith(self.extension):
            name += self.extension
        with open(name, 'r'+self.binary) as f:
            data = self.module.load(f)
        return data['data']

    def read_metadata(self, file_path, file_name):
        """
        Read metadata from a file.

        Parameters:
        - file_path (str): The path to the file.
        - file_name (str): The name of the file.

        Returns:
        - dict: The metadata read from the file.
        """
        name = file_path + file_name
        if not name.endswith(self.extension):
            name += self.extension
        with open(name, 'r'+self.binary) as f:
            data = self.module.load(f)
        return data['metadata']

def load():
    """
    Load an instance of the abstract format class.

    Returns:
    - An instance of the abstract format class.
    """
    # Return an instance of the MSE class
    return Format()