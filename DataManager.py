import os
import json

from abc import ABC
from enum import Enum

from DataManager import *

class DataFields:
    """
    This class stores the constants for the specific fields of the data you are saving (e.g. user_id, item_id).
    Extend this class to define the data fields.
    """

    IDENTIFIER = "identifier"

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
    """

    DATAPATH = None

    _DEFAULT_VALUES = {}
    """ Stored as `key: value`
     
        These values correspond to the constants in DataFields
     """

    def __init__(self, datapath: str):
        """
            Datapath should be a string that is a valid path to a directory. Use os.path.join to make it platform independent.
        """
        if isinstance(datapath, str):
            if not os.path.exists(datapath):
                os.makedirs(datapath)
            self.DATAPATH = datapath
        else:
            raise ValueError("datapath needs to be a string")
    
    @property
    def datapath(self):
        if isinstance(self.DATAPATH, str):
            return self.DATAPATH
        else:
            raise ValueError("Tried to retrieve null datapath")
        
    @property
    def getDefaultValues(self) -> dict:
        return self._DEFAULT_VALUES
        
    def getFormattedFilename(self, identifier: str) -> str:
        """
            Overwrite this function to change the format of file creation.

            This MUST return a string that is a valid file path (with the .json extension)

            WARNING: Overriding how files look may require you to override several other functions (depending on how your are formatting your names. Take a look at Example.py.). You are much better of using directories to sort data rather than formatting.
        """
        return os.path.join(self.datapath, f"{identifier}.json")
    
    def databaseExists(self, identifier: str) -> bool:
        """
        This function should check if the database exists.
        """
        path = self.getFormattedFilename(identifier)
        return os.path.exists(path)

    def getData(self, identifier: str, key: DataFields = None):
        """
        This function should fetch the data from the DB and return it.

        Returns `dict` unless a key is specified, in which case it returns the value of the key.
        """

        path = self.getFormattedFilename(identifier)

        if not self.databaseExists(identifier):
            raise DataManagerErrors.PathNotExists()
        
        with open(path, 'r') as file:
            data = json.load(file)

        # Validates all default keys exist.
        data |= {key: value for key, value in self.getDefaultValues.items() if key not in data} # Add any missing default values from `self.getDefaultValues()` to `data`
        data.setdefault(DataFields.IDENTIFIER, identifier) # Ensure `DataFields.IDENTIFIER` exists in `data`, setting it to `identifier` if missing

        path = self.getFormattedFilename(identifier)
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)

        if key is not None:
            if key not in data:
                raise DataManagerErrors.DataKeyNotExists(key)
            return data[key]
        return data

    def setData(self, identifier: str, field: DataFields, newVal) -> None:
        data = self.getData(identifier)
        data[str(field)] = newVal

        path = self.getFormattedFilename(identifier)
        try:
            with open(path, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception:
            raise DataManagerErrors.PathNotExists()

    def createDatabase(self, identifier: str):
        """
            This function should create the datatype in the DB.
        """
        path = self.getFormattedFilename(identifier)
        if self.databaseExists(identifier):
            raise DataManagerErrors.PathExists()
        else:
            with open(path, 'w') as file:
                json.dump({str(DataFields.IDENTIFIER): identifier}, file, indent=4)

    def deleteDatabase(self, identifier: str):
        """
            This function should delete the datatype from the DB.
        """
        path = self.getFormattedFilename(identifier)
        
        if not self.databaseExists(identifier):
            raise DataManagerErrors.PathNotExists()
        
        try:
            os.remove(path)
        except Exception as e:
            raise Exception(f"An error occurred while deleting the database: {str(e)}")
        
    def DANGER_DELETEALL(self):
        """
            Deletes entire database.

            WARNING: THIS DELETES THE ENTIRE DATAPATH FOLDER! Please ensure only data is stored here!
        """
        if not os.path.exists(self.datapath):
            raise DataManagerErrors.PathNotExists()

        try:
            # Remove all files in the datapath directory
            for filename in os.listdir(self.datapath):
                file_path = os.path.join(self.datapath, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    # If it's a directory, remove it recursively
                    os.rmdir(file_path)

            # Optionally, remove the datapath itself if it's empty
            os.rmdir(self.datapath)
        except Exception as e:
            raise Exception(f"An error occurred while deleting the entire database: {str(e)}")
