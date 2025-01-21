import pickle
from SWx_modules.file_management.formats.abstract_format import Format

class PKL (Format):

    def __init__(self):
        super(PKL, self).__init__()
        self.extension = '.pkl'
        self.module = pickle
        self.binary = 'b'

def load():
    """
    Load an instance of the PKL class.

    Returns:
    - An instance of the PKL class.
    """
    return PKL()

