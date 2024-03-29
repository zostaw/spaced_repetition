import pathlib
import sys

# directory reach
directory = str(pathlib.Path(__file__).parent.parent.resolve())

# setting path
sys.path.append(directory)

from SpacedRepetition import SpacedRepetition


db_name, number_of_boxes, records_per_box = "testdb", 3, 3
db = SpacedRepetition(db_name, number_of_boxes, records_per_box)


# boxes_list = db.ReturnAllBoxes()
# print(boxes_list)

db.PlaySession()
