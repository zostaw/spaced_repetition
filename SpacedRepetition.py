# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 12:00:00 2022

@author: zostaw
"""

from hashlib import new
import os
import sqlite3
import numpy as np
import random

#debugging library
from icecream import ic



# to import in another program: from SpacedRepetition ##which is file### import SpacedRepetition ##which is class###
class SpacedRepetition():

    # database class - it serves to store and manage elements (facts/quotse) and provides 
    # querries to shufle them, add, manage the daily boxes



#### init Methods

    def __init__(self, num_of_boxes=7, daily_limit=5, db_name="db_name"):

        self.db_name = db_name
        self.max_num_boxes = num_of_boxes
        # daily_limit - how many entries can be in a single box at a time (unless moved from another box)
        self.daily_limit = daily_limit
        self.init_db()
        self.assignment_type = np.squeeze(self.execute_one(''' SELECT Assignment_Type FROM Params LIMIT 1;'''))

    def init_db(self):
        #initiate database
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
    

        # name is a label for a record, 
        # record_visible is a part that can be shown immediatelly
        # record_hidden would be a second part of the record, for example a response to question, that one should not seeat first
        # Is_In_Use states whether the record is assigned to any box already
        # Days_In_Boxes is to represent how many times a record landed in boxes
        c.execute('''
            CREATE TABLE IF NOT EXISTS Records
            (
            [Record_Id] INTEGER PRIMARY KEY, 
            [Record_Name] TEXT NOT NULL DEFAULT "", 
            [Record_Visible] TEXT DEFAULT "", 
            [Record_Hidden] TEXT DEFAULT "", 
            [Is_In_Use] BOOLEAN DEFAULT 0, 
            [Days_In_Boxes] INTEGER DEFAULT 0
            )
            ''')
        
        c.execute('''CREATE UNIQUE INDEX IF NOT EXISTS Records_Content_Idx on Records(Record_Name, Record_Visible, Record_Hidden)''')

        c.execute('''
            CREATE TABLE IF NOT EXISTS BoxQueue
            ([Box_Id] INTEGER PRIMARY KEY)
            ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS Params
            ([Assignment_Type] TEXT default "random")
            ''')
        # generate Default config only once. Once it is generated, the parameters can be edited, they should not be overwritten by reinitializing the class.
        c.execute('''select rowid from Params limit 1;''')
        rowid = c.fetchone()
        ic(rowid)
        if rowid == None:
            c.execute('''
                INSERT INTO Params (rowid, Assignment_Type)
                VALUES (1, "random")
                ''')
        c.execute('''PRAGMA foreign_keys = ON;
        ''')

        conn.commit()

        self.CreateBox()

    def LoadParams(self):
        self.Type
        
#### Helping Methods
    def getParam(self, param_name):

        if not isinstance(param_name, str):
            raise ValueError("Wrong type of param_name: is " + str(type(param_name)) + " should be string.")

        db = self.db_name
        
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('''SELECT ''' + param_name + ''' FROM Params LIMIT 1''')
        result = c.fetchone()
        ic(str(np.squeeze(result)))
        
        c.close()

        output = np.squeeze(result)

        if output == None:
            raise ValueError("Parameter could not be found in Params table. Check if your parameter name is correct. The possible values are column names: " + str(self.execute_one('''select sql from sqlite_master where type = 'table' and name = 'Params';''')) + "\
            Check if table record was generated during initialization. If it does not exist you might need to reinitialize table Params.")

        return output

    def execute_one(self, querry):
        
        db = self.db_name
        
        with sqlite3.connect(db) as conn:
            c = conn.cursor()
            c.execute('''PRAGMA foreign_keys = ON;''')
            result = c.execute(querry)
            output = list(result)
            conn.commit()
        if conn:
            conn.close()
        
        return output

#### Record methods:
    def AddRecord(self, name, visible_text="", hidden_text=""):
        # adds new row to 
        db = self.db_name
        
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('''PRAGMA foreign_keys = ON;''')
        result = c.execute('''
            INSERT OR IGNORE INTO Records
            (Record_Name, Record_Visible, Record_Hidden)
            VALUES ("''' + name + '''",
            "''' + visible_text + '''",
            "''' + hidden_text + '''")
            ''')
        conn.commit()
        conn.close()

        Record_Id = int(np.squeeze(c.lastrowid))

        return Record_Id

    def RemoveRecord(self):
        pass

    def AssignRecord(self, record_id, box_id=None):
        # This method adds a Record to a box
        # by default Youngest Box is picked

        if not isinstance(record_id, int):
            raise ValueError("Wrong type of record_id: is " + str(type(record_id)) + " should be integer.")
        if not isinstance(box_id, int) and not None:
            raise ValueError("Wrong type of box_id: is " + str(type(box_id)) + " should be integer or None.")

        # Check if is not assigned
        in_use = int(np.squeeze(self.execute_one('''SELECT Is_In_Use from Records where Record_Id='''+ str(record_id) )))
        if in_use:
            print("The record " + str(record_id) + " is already in one of the boxes.")
            return None
        else:
            # Choose box
            if box_id == None:
                box_id = np.squeeze(self.execute_one('''select Box_Id from BoxQueue ORDER BY Box_Id DESC LIMIT 1'''))
            # Create box if zero
            if not box_id > 0 and self.max_num_boxes > 0:
                self.CreateBox()
            # Assign
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''PRAGMA foreign_keys = ON;''')
            c.execute('''SELECT COUNT(*) FROM Box''' + str(box_id) + ''';''')
            records_count = np.squeeze(c.fetchone())
            if not (records_count < self.daily_limit or None):
                print("Box" + str(box_id) + " is full. Adding overboard.")
            c.execute('''
                INSERT INTO Box''' + str(box_id) + '''
                ([Record_Id])
                VALUES (''' + str(record_id) + ''');
                ''')
            c.execute('''
                UPDATE Records SET Is_In_Use=1 where Record_Id='''+ str(record_id) +''';
                ''')
            c.execute('''
                UPDATE Records SET Days_In_Boxes = Days_In_Boxes + 1 where Record_Id='''+ str(record_id) +''';
                ''')

            conn.commit()
            conn.close()
        return int(record_id)

    def DischargeRecord(self, record_id, box_id):
        print("[DischargeRecord] record_id: " + str(record_id))
        if not isinstance(record_id, int):
            raise ValueError("Wrong type of record_id: is " + str(type(record_id)) + " should be integer.")
        if not isinstance(box_id, int):
            raise ValueError("Wrong type of box_: is " + str(type(box_id)) + " should be integer.")

        # remove Record from a Box
        print("Discharging Record (start) " + str(record_id) + " from Box " + str(box_id))
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''PRAGMA foreign_keys = ON;''')
        # remove from box
        command='''delete from Box''' + str(box_id) + ''' where Record_Id = '''+ str(record_id) + ''';'''
        print(command)
        c.execute('''delete from Box''' + str(box_id) + ''' where Record_Id = '''+ str(record_id) + ''';''')
        # activate for picking
        c.execute('''update Records set Is_In_Use=0 where Record_Id = '''+ str(record_id) + ''';''')
        conn.commit()
        print("Discharging Record (done) " + str(record_id) + " from Box " + str(box_id))
        

    def ReturnRecord(self, record_id):
        # output is list of elements
        # correct way to unpack:
        # id, name, visible, hidden, is_in_use, used_counter = db.ReturnRecord(id)

        if not isinstance(record_id, int):
            raise ValueError("Wrong type of record_id: is " + str(type(record_id)) + " should be integer.")

        record = self.execute_one('''
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Is_In_Use, Days_In_Boxes from Records where Record_Id='''+ str(record_id) +'''
            ''')
        return record[0]

    def PrintRecord(self, record_id):
        # print one
        if not isinstance(record_id, int):
            raise ValueError("Wrong type of record_id: is " + str(type(record_id)) + " should be integer.")

        [id, name, visible, hidden, is_in_use, used_counter] = self.ReturnRecord(record_id)
        print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")

    def ReturnAllRecords(self):
        # output is list of lists (for each column)
        # correct way to unpack:
        #records=db.ReturnAllRecords()
        #for record_id in range(len(records)):
        #    id, name, visible, hidden, is_in_use, used_counter = records[record_id]
        #    print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")

        records = self.execute_one('''
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Is_In_Use, Days_In_Boxes from Records
            ''')
        return records

    def PrintAllRecords(self):
        records=self.ReturnAllRecords()
        for record_id in range(len(records)):
            id, name, visible, hidden, is_in_use, used_counter = records[record_id]
            print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")



#### Box Methods

    def CreateBox(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
            insert into BoxQueue (Box_id) SELECT max(Box_id)+1 from BoxQueue;
            ''')
        Box_Id = np.squeeze(c.lastrowid)
        c.execute('''
            CREATE TABLE IF NOT EXISTS Box''' + str(Box_Id) + '''
            (
            [Record_Id] INTEGER PRIMARY KEY,
            FOREIGN KEY(Record_Id) REFERENCES Records(Record_Id)
            )
            ''')
        conn.commit()
        return int(Box_Id)

    def ReturnBox(self, box_id):
        # output is list of lists ( one line for each Record)
        # correct way to unpack - see ReturnAllRecords

        Box_Records = self.execute_one('''
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Is_In_Use, Days_In_Boxes from Records where Record_Id in (SELECT Record_Id from Box''' + str(box_id) +''')
            ''')

        #print(str(list(Box_Records)[1]))
        return list(Box_Records)

    def PrintBox(self, box_id):
        # prints name of Box and then list of Records in this Box

        
        Box_Records=self.ReturnBox(box_id)
        if not Box_Records: 
            print("Box" + str(box_id) + " is empty.")
            return None
        else:
            print("Box" + str(box_id) + ":")
            for record_id in range(len(Box_Records)):
                id, name, visible, hidden, is_in_use, used_counter = Box_Records[record_id]
                print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")

    def ReturnAllBoxes(self):
        # returns list of Boxes names as list
        output = self.execute_one('''select Box_Id from BoxQueue''')
        Boxes_Ids = np.squeeze(output)

        return Boxes_Ids

    def PrintAllBoxes(self):
        # prints Records of All Boxes
        for Box_Id in self.ReturnAllBoxes():
            self.PrintBox(Box_Id)
        
        
#### Interaction Methods

    def AssignNext(self, order_by=None):
        # random function - search for record that is not in boxes already
        # default order_by is stored in Param table under Assignment_Type
        if order_by == None:
            ic(str(self.getParam("Assignment_Type")))
            order_by = str(self.getParam("Assignment_Type"))

        box_id = int(np.squeeze(self.execute_one('''select Box_Id from BoxQueue ORDER BY Box_Id DESC LIMIT 1;''')))

        if not box_id > 0:
            box_id = int(np.squeeze(self.CreateBox()))

        if order_by == 'rarity_random':
                return "Not defined yet"
        elif order_by == 'random':
                record_id = self.execute_one('''SELECT Record_Id from Records where Is_In_Use = 0 ORDER BY RANDOM() LIMIT 1;''')
                if not record_id:
                    print("No unassigned records found.")
                else:
                    self.AssignRecord(int(np.squeeze(record_id)), box_id)
                return record_id
        elif order_by == None:
            return "order_by None, my fellow, please pick your new assignments manually by running AssignRecord(Record_Id)"
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
            random.shuffle(box)

        if limit == "daily_limit":
            limit = self.daily_limit
            box = box[:limit]

        clear = lambda: os.system('clear')       

        input("A box is full of questions. You will be tested, here it comes, good luck!")
        # Do-while emulation, AllCorrect = False for initiate run
        AllCorrect = False
        while not AllCorrect:
            # all are correct until one fails
            AllCorrect = True
            if order == "random":
                random.shuffle(box)
            for record in box:
                clear()
                print("Question: " + record[1] + record[2])
                response = input("Answer:  ")
                if response == record[3]:
                    print("You guessed it! The response is indeed '" + record[3] + "'. Congratulations!!!")
                else:
                    # Fail here!!! Hence all are no longer correct
                    AllCorrect = False
                    print("Not quite right, the correct response is '" + record[3] + "'")
                input("Continue...")
            if not AllCorrect:
                input("You made mistakes. Here try again and prove that you can do it!")
        input("You made it through the box!")
        return AllCorrect

    def PlaySession(self):
        # method that will provide the daily set of Repetition Session
        # it will print questions for each box in order and request an answer
        # single box will be shown in a loop until all answers are correct
        # once all answers are correct, it will once more ask them in a random manner and continue with the next box
        # a couple of questions from all boxes will be then presented in a random order once more after finishing with all boxes
        

        clear = lambda: os.system('clear')

        boxes_list = self.ReturnAllBoxes()
        all_boxed_records = []
        for box_id in boxes_list:
            box = self.ReturnBox(box_id)
            # play session on one box at a time
            self.testBox(box, 'random')
            # save into a list
            if not box == []:
                all_boxed_records += box

        input("You finished and succeeded on all boxes. An ultimate test comes. Random questions will be asked from all boxes to challenge you once again, this time with random questions.")
        self.testBox(all_boxed_records, 'random')

        

    def EoD_Rotation(self):
        # rotating boxes function

        # cleanup oldest box and initiate new

        # create new
        new_boxes_amnt = 1
        for i in range(new_boxes_amnt):
            self.CreateBox()

        # if reached max_days: delete first Boxes
        #box_count = np.squeeze(self.execute_one('''select count(Box_Id) from BoxQueue'''))
        
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''PRAGMA foreign_keys = ON;''')
        
        c.execute('''select Box_Id from BoxQueue''')
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
                    record_id = int(record[0])
                    print("record_id: " + str(record_id))
                    self.DischargeRecord(record_id, box_id)

                self.execute_one('''delete from BoxQueue where Box_Id = ''' + str(box_id) +''';''')
                self.execute_one('''drop table Box''' + str(box_id) +''';''')
                conn.commit()
                print("Removing box (commited): " + str(box_id))

            print(str(excess) + " boxes deleted from queue.")

        # assign new
        c.execute('''SELECT Box_Id FROM BoxQueue ORDER BY Box_Id DESC LIMIT 1;''')
        box_id = np.squeeze(c.fetchone())
        c.execute('''SELECT COUNT(*) FROM Box''' + str(box_id) + ''';''')
        records_count = np.squeeze(c.fetchone())
        while records_count < self.daily_limit:
            self.AssignNext()
            records_count += 1

        conn.close()






if __name__ == '__main__':
    db = SpacedRepetition(7, 5, "learning_words")

    #db.AddRecord("Oumi Janta", "If I can see you grove -- if you have fun -- I can see that you trully feel the music and feel the track -- And that makes you move much more beautiful", "")

    db.AddRecord("", "lasting for a very short time", "ephemeral")

    db.AddRecord("", "atrakcyjny, uwodzący", "alluring, enticing, captivating")

    db.AddRecord("", "hipnotyzujący", "mesmerizing")

    db.AddRecord("", "niewypowiedziane, nieznane", "innefable")

    db.AddRecord("", "overwhelmingly fearful", "petrified")

    db.AddRecord("", "a countless or extremally great number", "myriad")

    db.AddRecord("","person showing ability to speak fluently and coherently", "articulate")

    db.AddRecord("","nunchi", "the subtle art and ability to listen and gauge others' moods, it means 'eye force/power'")


    #rotation:
    # for i in range(10):
    #     db.EoD_Rotation()    

    # db.PrintAllBoxes()


    db.PlaySession()








