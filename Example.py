from DataManager import *

import os

class ExampleDataFields (DataFields):
    STRING = "string"
    NUMBER = "number"
    BOOL = "bool"
    pass

class ExampleDataManager (DataManager):
    _DEFAULT_VALUES = {
        ExampleDataFields.STRING: "example",
        ExampleDataFields.NUMBER: 1234,
        ExampleDataFields.BOOL: True
    }

    def __init__(self):
        super().__init__(os.path.join(os.path.dirname(__file__), "data")) # Forced the datapath here.


# Code from here point on.

breakpoint = lambda: input("\nPress Enter to continue. \n")

manager = ExampleDataManager()

identifier = input("Enter identifier: ")
if not manager.databaseExists(identifier):
    manager.createDatabase(identifier)

breakpoint()
# Get the data for "user123"
user_data = manager.getData(identifier)
print("User Data:", user_data)

breakpoint()
# Access the specific data key (e.g., STRING, NUMBER, BOOL)
user_string = manager.getData(identifier, ExampleDataFields.STRING)
print("User String:", user_string)

breakpoint()
# Set a new value for the STRING field
manager.setData(identifier, ExampleDataFields.STRING, "new_value_for_string")
updated_user_data = manager.getData(identifier)
print("Updated User Data:", updated_user_data)

breakpoint()
# Attempt to fetch a key that does not exist (will raise error)
try:
    invalid_key = manager.getData(identifier, "non_existent_key")
except DataManagerErrors.DataKeyNotExists as e:
    print("noKey Error:", e)

breakpoint()
# Attempt to create a database for an existing identifier (will raise error)
try:
    manager.createDatabase(identifier)
except DataManagerErrors.PathExists as e:
    print("repeatID Error:", e)

breakpoint()
# Attempt to delete the created database
manager.deleteDatabase(identifier)

# Attempt to access the deleted database
try:
    manager.getData(identifier)
except DataManagerErrors.PathNotExists as e:
    print("delete Error:", e)

breakpoint()

# Delete the entire database folder (...DataAPI\data). Once when it is still alive, once again after it is deleted.
while True:
    try:
        manager.DANGER_DELETEALL()
    except DataManagerErrors.PathNotExists as e:
        print("deleteall Error:", e)
        break
    except Exception as e:
        print("deleteall Error:", e)