import pathlib
import sys
from types import NoneType


# directory reach
directory = str(pathlib.Path(__file__).parent.parent.resolve())

# setting path
sys.path.append(directory)

from SpacedRepetition import SpacedRepetition


db_name, number_of_boxes, records_per_box = "testdb", 7, 5
db = SpacedRepetition(db_name, number_of_boxes, records_per_box)


for getter in [db.ReturnAllBoxesIds(), db.ReturnAllBoxes()]:
    if getter is []:
        raise ValueError("{getter.__name__} is Empty")
    if type(getter) is NoneType:
        raise ValueError("{getter.__name__} is NoneType")

print("ReturnAllBoxesIds: " + str(db.ReturnAllBoxesIds()))
print("ReturnAllBoxes: " + str(db.ReturnAllBoxes()))
# print("ReturnAllRecords: " + str(db.ReturnAllRecords()))
