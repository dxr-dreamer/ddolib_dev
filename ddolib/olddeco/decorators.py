from .core import DigitalObject,Relationship
from .dos import DataDigitalObject,FunctionDigitalObject, InstanceDigitalObject
from .connetion import storage_manager
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def DDO(metadata,IRS=None,doid=None):
    """
    Decorator to define a Data Digital Object (DDO).

    Parameters:
    metadata (dict): Metadata to attach to the data object.
    IRS,doid(optinal)

    Returns:
    function: The wrapped function that returns a WrappedDataObject.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            ddo = DataDigitalObject(data, metadata,IRS,doid)
            ddo.save()
            return ddo
        return wrapper
    return decorator




    
        
    
