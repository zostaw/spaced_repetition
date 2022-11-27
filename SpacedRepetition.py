# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 12:00:00 2022

@author: zostaw
"""

from hashlib import new
import os
from pathlib import Path
import sqlite3
from types import NoneType
import numpy as np
import random
from itertools import chain
import json

# debugging library
from icecream import ic

ic.disable()

DATASETS_DIR = Path(__file__).parent / "datasets"
SESSIONS_DIR = Path(__file__).parent / "sessions"

# to import in another program: from SpacedRepetition ##which is file### import SpacedRepetition ##which is class###
class SpacedRepetition:

    # database class - it serves to store and manage elements (facts/quotse) and provides
    # querries to shufle them, add, manage the daily boxes

    #### init Methods

    def __init__(
        self,
        session_id="default",
        dataset_name=None,
        num_of_boxes=7,
        daily_limit=5,
    ):
        """
        Args:
            session_id (string): unique session id - allows to track state of db
                                and API requests
            dataset_name (string): database is initiated from datasets files,
                                if not provided - empty database will be created
            num_of_boxes (int): total number of boxes in rotation
            daily_limit (int): limit number of records that are added into new box

        """

        if dataset_name:
            dataset_path = os.path.join(DATASETS_DIR, f"{dataset_name}.json")
            if os.path.exists(dataset_path):
                is_dataset = True

        if "is_dataset" in locals():
            db_name = f"{dataset_name}"
        else:
            db_name = "no-dataset"

        session_path = os.path.join(SESSIONS_DIR, session_id)

        db_path = os.path.join(session_path, db_name)

        if not os.path.exists(session_path):
            # Create a new session directory because it does not exist
            try:
                os.makedirs(session_path)
            except os:
                print(f"Path {session_path} could not be created.")

        self.db_path = db_path
        self.max_num_boxes = num_of_boxes
        # daily_limit - how many entries can be in a single box at a time (unless moved from another box)
        self.daily_limit = daily_limit
        self.init_db()

        if "is_dataset" in locals():
            self.LoadDataset(dataset_path)

        self.assignment_type = np.squeeze(
            self.execute_one(""" SELECT Assignment_Type FROM Params LIMIT 1;""")
        )

    def init_db(self):
        # initiate database
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # name is a label for a record,
        # record_visible is a part that can be shown immediatelly
        # record_hidden would be a second part of the record, for example a response to question, that one should not seeat first
        # Is_In_Use states whether the record is assigned to any box already
        # Days_In_Boxes is to represent how many times a record landed in boxes
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS Records
            (
            [Record_Id] INTEGER PRIMARY KEY,
            [Record_Name] TEXT NOT NULL DEFAULT "",
            [Record_Visible] TEXT DEFAULT "",
            [Record_Hidden] TEXT DEFAULT "",
            [Is_In_Use] BOOLEAN DEFAULT 0,
            [Days_In_Boxes] INTEGER DEFAULT 0
            )
            """
        )

        c.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS Records_Content_Idx on Records(Record_Name, Record_Visible, Record_Hidden)"""
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS BoxQueue
            ([Box_Id] INTEGER PRIMARY KEY)
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS Params
            ([Assignment_Type] TEXT default "random")
            """
        )
        # generate Default config only once. Once it is generated, the parameters can be edited, they should not be overwritten by reinitializing the class.
        c.execute("""select rowid from Params limit 1;""")
        rowid = c.fetchone()
        ic(rowid)
        if rowid == None:
            c.execute(
                """
                INSERT INTO Params (rowid, Assignment_Type)
                VALUES (1, "random")
                """
            )
        c.execute(
            """PRAGMA foreign_keys = ON;
        """
        )

        conn.commit()

        # commented out - the box should not be created on each connection
        # if it's needed for assigning record to empty box and it does not exist, the box should be created before
        # self.CreateBox()

    def LoadParams(self):
        self.Type

    #### Helping Methods
    def getParam(self, param_name):

        if not isinstance(param_name, str):
            raise ValueError(
                "Wrong type of param_name: is "
                + str(type(param_name))
                + " should be string."
            )

        db = self.db_path

        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("""SELECT """ + param_name + """ FROM Params LIMIT 1""")
        result = c.fetchone()
        ic(str(np.squeeze(result)))

        c.close()

        output = np.squeeze(result)

        if output == None:
            raise ValueError(
                "Parameter could not be found in Params table. Check if your parameter name is correct. The possible values are column names: "
                + str(
                    self.execute_one(
                        """select sql from sqlite_master where type = 'table' and name = 'Params';"""
                    )
                )
                + "\
            Check if table record was generated during initialization. If it does not exist you might need to reinitialize table Params."
            )

        return output

    def execute_one(self, querry):

        db = self.db_path

        with sqlite3.connect(db) as conn:
            c = conn.cursor()
            c.execute("""PRAGMA foreign_keys = ON;""")
            result = c.execute(querry)
            output = list(result)
            conn.commit()
        if conn:
            conn.close()

        return output

    #### Record methods:
    def AddRecord(self, name, visible_text="", hidden_text=""):
        # adds new row to
        db = self.db_path

        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute("""PRAGMA foreign_keys = ON;""")
        result = c.execute(
            '''
            INSERT OR IGNORE INTO Records
            (Record_Name, Record_Visible, Record_Hidden)
            VALUES ("'''
            + name
            + '''",
            "'''
            + visible_text
            + '''",
            "'''
            + hidden_text
            + """")
            """
        )
        conn.commit()
        conn.close()

        Record_Id = int(np.squeeze(c.lastrowid))

        return Record_Id

    def DeleteRecord(self, record_id):
        pass

    def AssignRecord(self, record_id, box_id=None):
        # This method adds a Record to a box
        # by default Youngest Box is picked

        if not isinstance(record_id, int):
            raise ValueError(
                "Wrong type of record_id: is "
                + str(type(record_id))
                + " should be integer."
            )
        if not isinstance(box_id, int) and not isinstance(box_id, (str, type(None))):
            raise ValueError(
                "Wrong type of box_id: is "
                + str(type(box_id))
                + " should be integer or None."
            )

        # Check if is not assigned
        in_use = int(
            np.squeeze(
                self.execute_one(
                    """SELECT Is_In_Use from Records where Record_Id="""
                    + str(record_id)
                )
            )
        )
        if in_use:
            print("The record " + str(record_id) + " is already in one of the boxes.")
            return None
        else:
            # Choose box
            if box_id == None:
                box_id = np.squeeze(
                    self.execute_one(
                        """select Box_Id from BoxQueue ORDER BY Box_Id DESC LIMIT 1"""
                    )
                )
            # Create box if zero
            if not box_id > 0 and self.max_num_boxes > 0:
                box_id = self.CreateBox()
            # Assign
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""PRAGMA foreign_keys = ON;""")
            c.execute("""SELECT COUNT(*) FROM Box""" + str(box_id) + """;""")
            records_count = np.squeeze(c.fetchone())
            if not (records_count < self.daily_limit or None):
                print("Box" + str(box_id) + " is full. Adding overboard.")
            c.execute(
                """
                INSERT INTO Box"""
                + str(box_id)
                + """
                ([Record_Id])
                VALUES ("""
                + str(record_id)
                + """);
                """
            )
            c.execute(
                """
                UPDATE Records SET Is_In_Use=1 where Record_Id="""
                + str(record_id)
                + """;
                """
            )
            c.execute(
                """
                UPDATE Records SET Days_In_Boxes = Days_In_Boxes + 1 where Record_Id="""
                + str(record_id)
                + """;
                """
            )

            conn.commit()
            conn.close()
        return int(record_id)

    def DischargeRecord(self, record_id, box_id):
        print("[DischargeRecord] record_id: " + str(record_id))
        if not isinstance(record_id, int):
            raise ValueError(
                "Wrong type of record_id: is "
                + str(type(record_id))
                + " should be integer."
            )
        if not isinstance(box_id, int):
            raise ValueError(
                "Wrong type of box_: is " + str(type(box_id)) + " should be integer."
            )

        # remove Record from a Box
        print(
            "Discharging Record (start) " + str(record_id) + " from Box " + str(box_id)
        )
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""PRAGMA foreign_keys = ON;""")
        # remove from box
        command = (
            """delete from Box"""
            + str(box_id)
            + """ where Record_Id = """
            + str(record_id)
            + """;"""
        )
        print(command)
        c.execute(
            """delete from Box"""
            + str(box_id)
            + """ where Record_Id = """
            + str(record_id)
            + """;"""
        )
        # activate for picking
        c.execute(
            """update Records set Is_In_Use=0 where Record_Id = """
            + str(record_id)
            + """;"""
        )
        conn.commit()
        print(
            "Discharging Record (done) " + str(record_id) + " from Box " + str(box_id)
        )

    def ReturnRecord(self, record_id):
        # output is list of elements
        # correct way to unpack:
        # id, name, visible, hidden, is_in_use, used_counter = db.ReturnRecord(id)

        if not isinstance(record_id, int):
            raise ValueError(
                "Wrong type of record_id: is "
                + str(type(record_id))
                + " should be integer."
            )

        record = self.execute_one(
            """
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Is_In_Use, Days_In_Boxes from Records where Record_Id="""
            + str(record_id)
            + """
            """
        )
        return record[0]

    def PrintRecord(self, record_id):
        # print one
        if not isinstance(record_id, int):
            raise ValueError(
                "Wrong type of record_id: is "
                + str(type(record_id))
                + " should be integer."
            )

        [id, name, visible, hidden, is_in_use, used_counter] = self.ReturnRecord(
            record_id
        )
        print(
            "id: "
            + str(id)
            + ", name: "
            + str(name)
            + ", visible: "
            + str(visible)
            + ", hidden: "
            + str(hidden)
            + ", Is in use: "
            + str(is_in_use)
            + ", used counter: "
            + str(used_counter)
            + " ."
        )

    def ReturnAllRecords(self):
        # output is list of lists (for each column)
        # correct way to unpack:
        # records=db.ReturnAllRecords()
        # for record_id in range(len(records)):
        #    id, name, visible, hidden, is_in_use, used_counter = records[record_id]
        #    print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")

        records = self.execute_one(
            """
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Is_In_Use, Days_In_Boxes from Records
            """
        )
        return records

    def PrintAllRecords(self):
        records = self.ReturnAllRecords()
        for record_id in range(len(records)):
            id, name, visible, hidden, is_in_use, used_counter = records[record_id]
            print(
                "id: "
                + str(id)
                + ", name: "
                + str(name)
                + ", visible: "
                + str(visible)
                + ", hidden: "
                + str(hidden)
                + ", Is in use: "
                + str(is_in_use)
                + ", used counter: "
                + str(used_counter)
                + " ."
            )

    #### Box Methods

    def CreateBox(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            """
            insert into BoxQueue (Box_id) SELECT max(Box_id)+1 from BoxQueue;
            """
        )
        Box_Id = np.squeeze(c.lastrowid)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS Box"""
            + str(Box_Id)
            + """
            (
            [Record_Id] INTEGER PRIMARY KEY,
            FOREIGN KEY(Record_Id) REFERENCES Records(Record_Id)
            )
            """
        )
        conn.commit()
        return int(Box_Id)

    def DeleteBox(self, box_id):
        # the method delets a Box entirely

        # release Records from the box
        box = self.ReturnBox(box_id)
        for record in box:
            self.DischargeRecord(record["id"], box_id)

        # release box from list
        self.execute_one(f"""delete from BoxQueue where Box_Id = {str(box_id)}""")
        # drop box table
        self.execute_one(f"""drop table Box{str(box_id)}""")

    def ReturnBox(self, box_id):
        # output is list of dicts (one line for each Record)
        # correct way to unpack - see ReturnAllRecords

        Box_listOflist = self.execute_one(
            f"""
            select Record_Id,
            Record_Name,
            Record_Visible,
            Record_Hidden,
            Is_In_Use,
            Days_In_Boxes
            FROM Records
            WHERE Record_Id
            IN (SELECT Record_Id from Box{str(box_id)})
            """
        )

        Box = []
        for record in Box_listOflist:
            record_dict = {
                "id": record[0],
                "name": record[1],
                "visible": record[2],
                "hidden": record[3],
                "is_in_use": record[4],
                "days_in_boxes": record[5],
            }
            Box.append(record_dict)

        return Box

    def PrintBox(self, box_id):
        # prints name of Box and then list of Records in this Box

        Box_Records = self.ReturnBox(box_id)
        if not Box_Records:
            print("Box" + str(box_id) + " is empty.")
            return None
        else:
            print("Box" + str(box_id) + ":")
            for record in Box_Records:
                print(
                    "id: "
                    + str(record["id"])
                    + ", name: "
                    + str(record["name"])
                    + ", visible: "
                    + str(record["visible"])
                    + ", hidden: "
                    + str(record["hidden"])
                    + ", is_in_use: "
                    + str(record["is_in_use"])
                    + ", days_in_boxes: "
                    + str(record["days_in_boxes"])
                    + " ."
                )

    def ReturnAllBoxesIds(self):
        # returns list of Boxes names as list
        output = self.execute_one("""select Box_Id from BoxQueue""")
        Boxes_Ids = np.squeeze(output)

        return Boxes_Ids

    def ReturnAllBoxes(self):
        # returns list of Boxes Records as list

        AllBoxes = []

        # the return type of ReturnAllBoxesIds can be: int, empty (ndarray) or a list
        # the for loop does not handle it well, therefore below are all 3 options handled

        # first initiate empty list
        boxes_list = []
        returned_list = self.ReturnAllBoxesIds().tolist()

        # if returned int, add it to list
        if isinstance(returned_list, int):
            boxes_list.append(returned_list)
        # if returned list, replace the empty one - append cannot be used, because empty elements are created
        if isinstance(returned_list, list):
            boxes_list = returned_list

        # if neither int nor list came from ReturnAllBoxes, then skip
        if not boxes_list:
            return None

        for box_id in boxes_list:
            box = self.ReturnBox(box_id)
            # save into a list if not empty
            if box == [] or type(box) is NoneType:
                continue
            AllBoxes.append(box)

        return AllBoxes

    def PrintAllBoxes(self):
        # prints Records of All Boxes
        for Box_Id in self.ReturnAllBoxesIds():
            self.PrintBox(Box_Id)

    #### datasets manipulation

    def SaveDataset(self, dataset_name):
        """Creates or overwrites existing dataset

        Args:
            dataset_name (string): name of dataset - will be stored in "datasets"
        """
        pass

    def LoadDataset(self, dataset_path):
        """Loads existing dataset

        Args:
            dataset_path (string): place in which datasets are located, they must be in format of json and each should contain dictionaries "name", "visible" and "hidden"
        """

        # open json file
        with open(dataset_path, "r") as file:
            data = json.load(file)

        for id in range(len(data["name"])):
            self.AddRecord(
                data["name"][str(id)], data["visible"][str(id)], data["hidden"][str(id)]
            )

    #### Interaction Methods

    def AssignNext(self, order_by=None):
        """random function - search for record that is not in boxes already
        default order_by is stored in Param table under Assignment_Type

        possible order_by:
        None - default
        random - equal distribution
        rarity_random - [not implemented] pick records that were placed rarely in boxes
        """
        if order_by == None:
            ic(str(self.getParam("Assignment_Type")))
            order_by = str(self.getParam("Assignment_Type"))

        box_id_querry = self.execute_one(
            """select Box_Id from BoxQueue ORDER BY Box_Id DESC LIMIT 1;"""
        )
        ic(box_id_querry)

        if box_id_querry:
            box_id = int(np.squeeze(box_id_querry))
        else:
            box_id = int(np.squeeze(self.CreateBox()))

        if order_by == "rarity_random":
            return "This order option is not defined"
        elif order_by == "random":
            record_id = self.execute_one(
                """SELECT Record_Id from Records where Is_In_Use = 0 ORDER BY RANDOM() LIMIT 1;"""
            )
            if not record_id:
                print("No unassigned records found.")
            else:
                self.AssignRecord(int(np.squeeze(record_id)), box_id)
            return record_id
        elif order_by == None:
            return "order_by None, my fellow, pick your new assignments manually by running AssignRecord(Record_Id)"
        else:
            return "Wrong order_by, should be: 'infrequent' or 'random'"

    def testBox(self, box, order="standard", limit="no"):
        # test memory on a box, it will repeat records until you get all right
        # parameters:
        # box - list of records
        # order - either standard (as provided) or random (shuffled)
        # limit - how many questiosn should be asked - possibleoptions:
        #         "no" - not limited
        #         "daily_limit" - self.daily_limit will be applied

        if box == []:
            print("Box is empty!")
            return None

        if order == "random":
            ic("random, shuffling")
            random.shuffle(box)

        if limit == "daily_limit":
            limit = self.daily_limit
            box = box[:limit]

        clear = lambda: os.system("clear")

        input(
            "A box is full of questions. You will be tested, here it comes, good luck!"
        )
        # Do-while emulation, AllCorrect = False for initiate run
        AllCorrect = False
        mistakes_counter = 0
        while not AllCorrect:
            # all are correct until one fails
            AllCorrect = True
            # reshuffle every time
            if order == "random" and mistakes_counter:
                random.shuffle(box)
            for record in box:
                clear()
                print(record["name"] + "-> Question: " + record["visible"])
                response = input("Answer:  ")
                if response == record["hidden"]:
                    print(
                        f"You guessed it! The response is indeed '"
                        + response
                        + "'. Congratulations!!!"
                    )
                else:
                    # Fail here!!! Hence all are no longer correct
                    AllCorrect = False
                    mistakes_counter += 1
                    print(
                        "Not quite right, the correct response is '"
                        + record["hidden"]
                        + "'"
                    )
                input("Continue...")
            if not AllCorrect:
                input("You made mistakes. Here try again and prove that you can do it!")
        return AllCorrect

    def PlaySession(self):
        # method that will provide the daily set of Repetition Session
        # it will print questions for each box in order and request an answer
        # single box will be shown in a loop until all answers are correct (testBox())
        # once all answers are correct, it will once more ask them in a random manner and continue with the next box
        # a couple of questions from all boxes will be then presented in a random order once more after finishing with all boxes

        clear = lambda: os.system("clear")

        all_boxed_records = self.ReturnAllBoxes()

        if not all_boxed_records:
            print("There are no boxes, initiate first")
            return

        no_boxes = len(all_boxed_records)
        print(f"You'll be tested against {no_boxes} boxes.")

        for box_id in range(no_boxes):
            self.testBox(all_boxed_records[box_id], "random")
            input("You made it through the box!")

        input(
            "You finished and succeeded on all boxes. An ultimate test comes. Random questions will be asked from all boxes to challenge you once again, this time with random questions."
        )
        # all_boxes_records is nested list, for the final test, all records should be together
        all_boxed_records = list(chain(*all_boxed_records))
        self.testBox(all_boxed_records, "random")
        print("Congratulations!!! You made it till the end. How impressive <3")

    def EoD_Rotation(self):
        """
        EoD_Rotation is a batch method, that simulates rotation of boxes.
        If there are no boxes, new one is created.
        Every call of this method will create a new box and initiate it with some of the unassigned records.
        The number of records that will be assigned is defined by `daily_limit`, while the maximum number of boxes by `num_of_boxes`.
        After `num_of_boxes` is reached, the oldest box will be dropped.

        """

        # create new
        new_boxes_amnt = 1
        for i in range(new_boxes_amnt):
            self.CreateBox()

        # if reached max_days: delete first Boxes
        # box_count = np.squeeze(self.execute_one('''select count(Box_Id) from BoxQueue'''))

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""PRAGMA foreign_keys = ON;""")

        c.execute("""select Box_Id from BoxQueue""")
        boxes_list = c.fetchall()
        box_count = len(boxes_list)

        print("max_num_boxes " + str(self.max_num_boxes))
        print("box_count: " + str(box_count))
        excess = box_count - self.max_num_boxes
        print("excess: " + str(excess))
        if excess > 0:
            for excess_id in range(excess):
                box_id = int(np.squeeze(boxes_list[excess_id]))
                print("Removing box (start): " + str(box_id))
                print("Removing records")
                for record in self.ReturnBox(box_id):
                    self.DischargeRecord(record["id"], box_id)

                self.execute_one(
                    """delete from BoxQueue where Box_Id = """ + str(box_id) + """;"""
                )
                self.execute_one("""drop table Box""" + str(box_id) + """;""")
                conn.commit()
                print("Removing box (commited): " + str(box_id))

            print(str(excess) + " boxes deleted from queue.")

        # assign new
        c.execute("""SELECT Box_Id FROM BoxQueue ORDER BY Box_Id DESC LIMIT 1;""")
        box_id = np.squeeze(c.fetchone())
        c.execute("""SELECT COUNT(*) FROM Box""" + str(box_id) + """;""")
        records_count = np.squeeze(c.fetchone())
        while records_count < self.daily_limit:
            self.AssignNext()
            records_count += 1

        conn.close()


if __name__ == "__main__":

    sr = SpacedRepetition(dataset_name="test_quotes")

    sr.EoD_Rotation()

    sr.PlaySession()
