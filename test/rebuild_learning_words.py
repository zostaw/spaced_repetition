import pathlib
import sys
import json
import pandas as pd
import os

# directory reach
directory = str(pathlib.Path(__file__).parent.parent.resolve())

# setting path
sys.path.append(directory)

from SpacedRepetition import SpacedRepetition


db_name, number_of_boxes, records_per_box = "learning_words", 4, 4

# cleanup database if exists
db_os_path = os.path.join(directory, db_name)
if os.path.exists(db_os_path):
    os.remove(db_os_path)

db = SpacedRepetition(db_name)

# open json file
with open("./datasets/test_quotes.json", "r") as file:
    data = json.load(file)

# json dictionary
# print(data["visible"]["0"])

print("Adding " + str(len(data["visible"])) + " records")

for id in range(len(data["visible"])):
    added = db.AddRecord(
        data["name"][f"{id}"], data["visible"][f"{id}"], data["hidden"][f"{id}"]
    )
    if added:
        print(
            "Record { \n"
            + data["name"][f"{id}"]
            + "\n"
            + data["visible"][f"{id}"]
            + "\n"
            + data["hidden"][f"{id}"]
            + "\n } was added.\n"
        )
    else:
        print("Could not add the record this time. Is it already present in db?")


for i in range(number_of_boxes):
    db.EoD_Rotation()
