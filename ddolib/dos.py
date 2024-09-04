from .core import DigitalObject,Relationship
import logging

class DataDigitalObject(DigitalObject):
    """
    Class representing a Data Digital Object (DDO).

    Inherits from DigitalObject.

    Attributes:
    data (any): The main content of the data digital object.
    metadata (dict): Metadata associated with the data digital object.
    doid (str): Unique identifier for the data digital object.
    """
    def __init__(self, data, metadata, IRS=None,doid=None):
        """
        Initializes a DataDigitalObject.

        Parameters:
        data (any): The main content of the data digital object.
        metadata (dict): Metadata associated with the data digital object.
        IRS(IdentifierResolutionService,optional): IRS which generate doid for this ddo. 
        doid (str, optional): Unique identifier for the data digital object.
        """
        if IRS and doid:
            logging.error(f"IRS and doid can't be assigned at the same time.")
            return False
        
        super().__init__(data, metadata, doid)
        if IRS:
            self.get_doid(IRS)
    

class FunctionDigitalObject(DigitalObject):
    """
    Class representing a Function Digital Object (FDO).

    Inherits from DigitalObject.

    Attributes:
    func (function): The function associated with the function digital object.
    metadata (dict): Metadata specific to the function digital object.
    """
    def __init__(self, func, metadata,iid=None, doid=None):
        """
        Initializes a FunctionDigitalObject.

        Parameters:
        func (function): The function associated with the function digital object.
        metadata (dict): Metadata specific to the function digital object.
        doid (str, optional): Unique identifier for the function digital object.
        """
        super().__init__(func, metadata, iid, doid)
    
    

class InstanceDigitalObject:
    """
    Class representing an Instance Data Object (IDO).

    Attributes:
    ddos (list): List of data digital objects in the instance.
    fdos (list): List of function digital objects in the instance.
    relationships (list): List of relationships between DOs.
    external_server (str): Address of the external registration server.
    """
    def __init__(self):
        """
        Initializes an InstanceDataObject.
        """
        pass

    def set_external_server(self, server):
        """
        Sets the external registration server address.

        Parameters:
        server (str): External server address.
        """
        pass

    def register_all(self):
        """
        Registers all DOs and relationships with the external server.
        """
        pass

    def add_ddo(self, ddo):
        """
        Adds a DDO to the instance.

        Parameters:
        ddo (DataObject): The data digital object to add.
        """
        pass

    def add_fdo(self, fdo):
        """
        Adds a FDO to the instance.

        Parameters:
        fdo (FunctionDataObject): The function digital object to add.
        """
        pass

    def add_relationship(self, rel):
        """
        Adds a relationship to the instance.

        Parameters:
        rel (Relationship): The relationship to add.
        """
        pass