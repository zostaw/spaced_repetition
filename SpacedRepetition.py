# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 12:00:00 2022

@author: zostaw
"""

from hashlib import new
import os
import sqlite3
import numpy as np


class SpacedRepetition():

    # database class - it serves to store and manage elements (facts/quotse) and provides 
    # querries to shufle them, add, manage the daily boxes



#### init Methods

    def __init__(self, num_of_boxes=7, db_name="db_name"):
        self.db_name = db_name
        self.max_num_boxes = num_of_boxes
        self.init_db()

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
            [Record_Name] TEXT NOT NULL, 
            [Record_Visible] TEXT DEFAULT "", 
            [Record_Hidden] TEXT DEFAULT "", 
            [Is_In_Use] BOOLEAN DEFAULT 0, 
            [Days_In_Boxes] INTEGER DEFAULT 0
            )
            ''')
        

        c.execute('''
            CREATE TABLE IF NOT EXISTS BoxQueue
            ([Box_Id] INTEGER PRIMARY KEY)
            ''')
        c.execute('''PRAGMA foreign_keys = ON;
        ''')

        conn.commit()

        self.CreateBox()
        
#### Helping Methods
    def execute_one(self, querry):
        
        db = self.db_name
        
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('''PRAGMA foreign_keys = ON;''')
        result = c.execute(querry)
        conn.commit()
        
        return list(result)

#### Record methods:
    def AddRecord(self, name, visible_text="", hidden_text=""):
        self.execute_one('''
            INSERT INTO Records
            (Record_Name, Record_Visible, Record_Hidden)
            VALUES ("''' + name + '''",
            "''' + visible_text + '''",
            "''' + hidden_text + '''")
            ''')

    def RemoveRecord(self):
        pass

    def AssignRecord(self, record_id, box_id=None):
        # This method adds a Record to a box

        # Check if is not assigned
        in_use = np.squeeze(self.execute_one('''SELECT Is_In_Use from Records where Record_Id='''+ str(record_id) ))
        if in_use:
            print("The record " + str(record_id) + " is already in one of the boxes.")
            return 
        else:
            # Choose box
            if box_id == None:
                box_id = np.squeeze(self.execute_one('''select Box_Id from BoxQueue limit 1'''))
            # Create box if zero
            if not box_id > 0 and self.max_num_boxes > 0:
                self.CreateBox()
            # Assign
            conn = sqlite3.connect(self.db_name)
            c = conn.cursor()
            c.execute('''PRAGMA foreign_keys = ON;''')
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

    def DischargeRecord(self, record_id, box_id):
        # remove Record from a Box
        print("Discharging Record " + str(record_id) + " from Box " + str(box_id))
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''PRAGMA foreign_keys = ON;''')
        # remove from box
        c.execute('''delete from Box''' + str(box_id) + '''where Record_Id = '''+ str(record_id) + ''';''')
        # activate for picking
        c.execute('''update Records set Is_In_Use=0 where Record_Id = '''+ str(record_id) + ''';''')
        conn.commit()
        

    def ReturnRecord(self, record_id):
        # output is list of elements
        # correct way to unpack:
        # id, name, visible, hidden, is_in_use, used_counter = db.ReturnRecord(id)

        record = self.execute_one('''
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Is_In_Use, Days_In_Boxes from Records where Record_Id='''+ str(record_id) +'''
            ''')
        return record[0]

    def PrintRecord(self, record_id):
        # print one
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
        Box_Id = c.lastrowid
        c.execute('''
            CREATE TABLE IF NOT EXISTS Box''' + str(Box_Id) + '''
            (
            [Record_Id] INTEGER PRIMARY KEY,
            FOREIGN KEY(Record_Id) REFERENCES Records(Record_Id)
            )
            ''')
        conn.commit()
        return Box_Id

    def ReturnBox(self, box_id):
        # output is list of lists ( one line for each Record)
        # correct way to unpack - see ReturnAllRecords

        Box_Records = self.execute_one('''
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Is_In_Use, Days_In_Boxes from Records where Record_Id in (SELECT Record_Id from Box''' + str(box_id) +''')
            ''')
        return Box_Records

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

    def AssignNext(self):
        #random function - search for record that is not in boxes already
        pass

    def PlaySession(self):
        # method that will provide the daily set of Repetition Session
        pass

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
                box_id = np.squeeze(boxes_list[excess_id])
                print("Removing box (start): " + str(box_id))
                for record_id in self.ReturnBox(box_id):
                    self.DischargeRecord(record_id, box_id)
                self.execute_one('''delete from BoxQueue where Box_Id in (select Box_Id from BoxQueue limit '''+ str(excess)  +''');''')
                conn.commit()
                print("Removing box (commited): " + str(box_id))

            print(str(excess) + " boxes deleted from queue.")






if __name__ == '__main__':
    db = SpacedRepetition()
    db.AddRecord("Oumi Janta", "If I can see you grove -- if you have fun -- I can see that you trully feel the music and feel the track -- And that makes you move much more beautiful", "")

    db.AddRecord("Microjournaling", "", "")

    db.AddRecord("alluring", "alluring", "atrakcyjny")

    db.AssignRecord(1, 1)
    db.AssignRecord(2, 1)

    db.EoD_Rotation()
    #db.PrintBox(1)

    db.AssignRecord(1, 1)
    db.AssignRecord(2, 1)

    db.PrintAllBoxes()









