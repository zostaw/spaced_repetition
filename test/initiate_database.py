import pathlib
import sys
import json
import pandas as pd

# directory reach
directory = str(pathlib.Path(__file__).parent.parent.resolve())

# setting path
sys.path.append(directory)

from SpacedRepetition import SpacedRepetition


db_name = "testdb" #, number_of_boxes = 7, records_per_box = 5
db = SpacedRepetition(db_name)

# open json file
with open('./datasets/test_quotes.json','r') as file:
    data = json.load(file)

# json dictionary
#print(data["visible"]["0"])

print("Adding " + str(len(data["visible"])) + " records")

for id in range(len(data["visible"])):
    added = db.AddRecord(data["name"][f"{id}"], data["visible"][f"{id}"], data["hidden"][f"{id}"])
    if added:
        print("Record { \n" + data["name"][f"{id}"] + "\n" + data["visible"][f"{id}"] + "\n" + data["hidden"][f"{id}"] + "\n } was added.\n")
    else:
        print("Could not add the record this time. Is it already present in db?")





