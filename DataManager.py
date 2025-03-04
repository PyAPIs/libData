import os
import json

from abc import ABC, abstractmethod
from enum import Enum

from DataManager import *

class DataFields (ABC):
    """
    This class stores the constants for the specific fields of the data you are saving (e.g. user_id, item_id).
    Extend this class to define the data fields.
    """

    IDENTIFIER = "identifier" # Identifier must exist as a data field.
    pass

class DataManagerErrors:
    """
        This class stores the error codes for the DataManager class. 
    """

    class PathExists(Exception):
        """
            This exception is raised when the path already exists.
        """
        
        def __init__(self, msg: str = None):
            super().__init__("Path already exists" + (f": {msg}" if msg else ""))

    class PathNotExists(Exception):
        """
            This exception is raised when the path does not exist.
        """
        
        def __init__(self, msg: str = None):
            super().__init__("Path does not exist" + (f": {msg}" if msg else ""))

    class DataKeyNotExists(Exception):
        """
            This exception is raised when the data key does not exist.
        """
        
        def __init__(self, key: str, msg: str = None):
            super().__init__(f"Data key {key} does not exist" + (f": {msg}" if msg else ""))

class DataManager (ABC):
    """
        This class is the abstract class for the DataManager. It is responsible for handling the data storage and retrieval.
        
        You will not be required to extend this class if you do not want to modify the data storage and retrieval. Simply pass the datapath through while instantiating this class and it should work.
        
        Extend this class if you want to make any edits to how data is saved (for example for `getFormattedFileType()`). Otherwise, simply instantiating this object should allow you to use the manager.
            e.g. UserDataManager (DataManager), GameDataManager (DataManager), 

        You need one data manager for each data type you are saving. This is because the data manager is responsible for the data storage and retrieval.

        If you want any quick functions to get or set data, extend this class and add the functions.
        Please note all functions must use the `identifier` to identify the data type, as this class does not house that infomation and is only responsible for the data storage and retrieval.
        
        Example:
        ```python
            def getPassword(self, identifier: str) -> str:
                return self.getData(identifier, DataFields.PASSWORD)
        ```
        (Note: Please remember to add all constants to an extension of the DataFields class)

        Definitions:
            Please take a look at the following definitions to adhere to existing naming conventions.
            - Datapath (DP): The folder in which a database is running (for example, `...\\root\\data\\`)
            - Database (DB): Databases are based on their assigned DP. They are responsible for the data manipulation within this path.
            - Datafile/document (DD): Databases store datafiles. The datafiles are (JSON) documents that store all of the data attached to an identifier.
            - DataField (DF): An enum class storing all of the data a Data Document will store through consts. Data can only be accessed through there consts.
    """

    _DATAPATH = None

    def __init__(self, datapath: str):
        """
            Datapath should be a string that is a valid path to a directory. Use os.path.join to make it platform independent.
        """

        if not isinstance(datapath, str): # Throw error if datapath type is incorrect
            raise ValueError("datapath needs to be a string")
    
        if not os.path.exists(datapath):
            os.makedirs(datapath) # Make the directory if it does not exist. This will also throw an error if a datapath style is incorrect.
        
        self._DATAPATH = datapath

    @property
    def datapath(self):
        if isinstance(self._DATAPATH, str):
            return self._DATAPATH
        else:
            raise ValueError(f"Tried to retrieve {type(self._DATAPATH)} datapath")
    
    def getDefaultValues(self) -> dict:
        """ Override this function to define the default (required) values of every datafile in a database. 
        
        Stored as `key: value`. These values correspond to the constants in DataFields. All DataFiles MUST have these values. DDs lacking any of the set keys will be repaired and set to the default state set here.

        Note that `DataFields.Identifier` already exists as a defalt value.
        """
        return {} # Default an empty dictionary here in the base class. This function is intended to be overwritten.
        
    def getFormattedFilename(self, identifier: str) -> str:
        """ Override this function to change the format of file creation.

            This MUST return a string that is a valid file path (with the .json extension)

            WARNING: Overriding how files look may require you to override several other functions (depending on how your are formatting your names. Take a look at Example.py.). You are much better of using databases within databases to sort data rather than formatting.
        """
        return os.path.join(self.datapath, f"{identifier}.json")
    
    def datafileExists(self, identifier: str) -> bool:
        """ This function returns if a datafile to an identifier exists. """
        path = self.getFormattedFilename(identifier) # Format filename for uniformity.
        return os.path.exists(path)

    def getData(self, identifier: str, key: DataFields = None):
        """
        This function should fetch the data from a datafile and return it.

        Returns `dict` unless a key is specified, in which case it returns the value of the key.
        """

        path = self.getFormattedFilename(identifier) # Get formatted filepath

        if not self.datafileExists(identifier):
            raise DataManagerErrors.PathNotExists() # Raise targetted error
        
        with open(path, 'r') as file: # Read contents of a file and save it to the data variable
            data = json.load(file)

        defaults = self.getDefaultValues() or {} # Ensure getDefaultValues() returns a dictionary (use empty dictionary if None)

        data.update({key: value for key, value in defaults.items() if key not in data}) # Merge missing default values from getDefaultValues into the data

        data.setdefault(DataFields.IDENTIFIER, identifier) # Ensure `DataFields.IDENTIFIER` exists in `data`, setting it to `identifier` if missing

        with open(path, 'w') as file: # Write the default values for missing keys
            json.dump(data, file, indent=4)

        if key is not None:
            if key not in data: # If the key does not exist return a targetted error
                raise DataManagerErrors.DataKeyNotExists(str(key))
            return data[key] # If a key was specified, return the value.
        return data # If no key was specified, return the data as a dictionary.

    def setData(self, identifier: str, field: DataFields, newVal) -> None:
        """ Sets a value to a field in a datafile. Assumes the newVal is a valid value for the field."""
        data = self.getData(identifier) # Get a dictionary of the data
        data[str(field)] = newVal # Set (or create) a key to the new value specified

        path = self.getFormattedFilename(identifier)
        try:
            with open(path, 'w') as file: # Override the new copy of the data with the new information on the old one.
                json.dump(data, file, indent=4)
        except Exception as e: # Raise a targetted PathNotExists error if anything goes wrong.
            raise DataManagerErrors.PathNotExists(str(e))

    def createDatafile(self, identifier: str):
        if self.datafileExists(identifier):  # Check if the datafile already exists
            raise DataManagerErrors.PathExists()
        else:
            path = self.getFormattedFilename(identifier)  # Get the formatted filename
            data = {str(DataFields.IDENTIFIER): identifier}
            data.update(self.getDefaultValues())  # Add the default values to the data when creating the datafile.
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)  # Write the combined data into the file.


    def deleteDatafile(self, identifier: str):
        """
            Delete a datafile from the database.
        """
        path = self.getFormattedFilename(identifier) # Get path
        
        if not self.datafileExists(identifier): # Ensure the path exists before deleting it
            raise DataManagerErrors.PathNotExists()
        
        try:
            os.remove(path) # Delete the path
        except Exception as e: # Raise any errors that may arrise.
            raise Exception(f"An error occurred while deleting the database: {str(e)}")
        
    def DANGER_DELETEALL(self):
        """
            Deletes the entire database.

            WARNING: THIS DELETES THE ENTIRE DATAPATH FOLDER! Please ensure only data is stored here!
        """

        if not os.path.exists(self.datapath): # Ensures the datapath exists before deleting it.
            raise DataManagerErrors.PathNotExists()

        try:
            # Remove all files in the datapath directory
            for filename in os.listdir(self.datapath): # Cycle through the contents of a directory
                file_path = os.path.join(self.datapath, filename) # Get the filepath of an item of the contents.
                if os.path.isfile(file_path): # Check if item is a file
                    os.remove(file_path) # If it is a file, remove the file.
                elif os.path.isdir(file_path): # Check if item is a directory
                    os.rmdir(file_path) # If it's a directory, remove it recursively

            os.rmdir(self.datapath) # Delete the datapath itself after it's all over.
        except Exception as e: # Raise any errors that my arrise.
            raise Exception(f"An error occurred while deleting the entire database: {str(e)}")
