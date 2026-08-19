from datacube import Datacube
from constants import constants

class BaseODCService:
    def __init__(self, dc: Datacube=None):
        #initialize Datacube as an object
        self.dc = dc if dc is not None else Datacube(app='Hellas_Cube')
        #initializing the constants to get them throughout
        self.const = constants