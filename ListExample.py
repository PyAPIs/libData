from DataManager import *

import os

class ExampleDataFields (DataFields):
    STRING = "string"
    NUMBER = "number"
    BOOL = "bool"
    pass

class ExampleDataManager (DataManager):
    def __init__(self):
        super().__init__(os.path.join(os.path.dirname(__file__), "data"), self.DatabaseType.LIST) # Forced the datapath here.

# Code from here point on.

breakpoint = lambda: input("\nPress Enter to continue. \n")

manager = ExampleDataManager()

identifier = input("Enter identifier: ")
if not manager.datafileExists(identifier):
    manager.createDatafile(identifier)

breakpoint()
# Get the data for "user123"
user_data = manager.getData(identifier)
print("User Data:", user_data)

breakpoint()
# Add data to the datafile
manager.addItem(identifier, "apple")
manager.addItem(identifier, "banana")
manager.addItem(identifier, "carrot")

print("User data after adding info:", manager.getData(identifier))

breakpoint()
# Attempt to create a database for an existing identifier (will raise error)
try:
    manager.createDatafile(identifier)
except DataManagerErrors.PathExists as e:
    print("repeatID Error:", e)

breakpoint()
# Attempt to delete the created database
manager.deleteDatafile(identifier)

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
        break