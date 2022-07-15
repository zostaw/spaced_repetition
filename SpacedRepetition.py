# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 12:00:00 2022

@author: zostaw
"""

import os
import sqlite3
import numpy as np


class SpacedRepetition():

    # database class - it serves to store and manage elements (facts/quotse) and provides 
    # querries to shufle them, add, manage the daily boxes

    spaced_rep_db = 'spaced_rep_db'

    def execute_one(self, querry, db=spaced_rep_db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute('''PRAGMA foreign_keys = ON;''')
        result = c.execute(querry)
        conn.commit()
        
        return list(result)

    def CreateBox(self):
        conn = sqlite3.connect(SpacedRepetition.spaced_rep_db)
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

    def init_db(self):
        #initiate database
        conn = sqlite3.connect(SpacedRepetition.spaced_rep_db)
        c = conn.cursor()
    

        # name is a label for a record, 
        # record_visible is a part that can be shown immediatelly
        # record_hidden would be a second part of the record, for example a response to question, that one should not seeat first
        # record_is_in_use states whether the record is assigned to any box already
        # record_used_counter is to represent how many times a record landed in boxes
        c.execute('''
            CREATE TABLE IF NOT EXISTS Records
            (
            [Record_Id] INTEGER PRIMARY KEY, 
            [Record_Name] TEXT NOT NULL, 
            [Record_Visible] TEXT DEFAULT "", 
            [Record_Hidden] TEXT DEFAULT "", 
            [Record_Is_In_Use] BOOLEAN DEFAULT 0, 
            [Record_Used_Counter] INTEGER DEFAULT 0
            )
            ''')
        

        c.execute('''
            CREATE TABLE IF NOT EXISTS BoxQueue
            ([Box_Id] INTEGER PRIMARY KEY)
            ''')
        c.execute('''PRAGMA foreign_keys = ON;
        ''')

        #print(str(list(c.execute('''PRAGMA foreign_keys;
        #'''))))

        conn.commit()

        for num in range(self.num_of_boxes):
            self.CreateBox()
        """            c.execute('''
                insert into BoxQueue (Box_id) SELECT max(Box_id)+1 from BoxQueue;
                ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS Box''' + str(num) + '''
                (
                [Record_Id_Id] INTEGER PRIMARY KEY, 
                [Record_Id] INTEGER,
                FOREIGN KEY(Record_Id) REFERENCES Records(Record_Id)
                )
                ''') """
        



    def AddRecord(self, name, visible_text="", hidden_text=""):
        self.execute_one('''
            INSERT INTO Records
            (Record_Name, Record_Visible, Record_Hidden)
            VALUES ("''' + name + '''",
            "''' + visible_text + '''",
            "''' + hidden_text + '''")
            ''')

    def AssignRecord(self, record_id, box_id=1):
        in_use = self.execute_one('''SELECT Record_Is_In_Use from Records where Record_Id='''+ str(record_id) )
        if in_use[0][0]:
            print("The record " + str(record_id) + " is already in one of the boxes.")
            return 
        else:
            conn = sqlite3.connect(SpacedRepetition.spaced_rep_db)
            c = conn.cursor()
            c.execute('''PRAGMA foreign_keys = ON;''')
            c.execute('''
                INSERT INTO Box''' + str(box_id) + '''
                ([Record_Id])
                VALUES (''' + str(record_id) + ''');
                ''')
            c.execute('''
                UPDATE Records SET Record_Is_In_Use=1 where Record_Id='''+ str(record_id) +''';
                ''')
            c.execute('''
                UPDATE Records SET Record_Used_Counter = Record_Used_Counter + 1 where Record_Id='''+ str(record_id) +''';
                ''')
            conn.commit()
    
    def RemoveRecord(self):
        pass


    def ReturnRecord(self, record_id):
        # output is list of elements
        # correct way to unpack:
        # id, name, visible, hidden, is_in_use, used_counter = db.ReturnRecord(id)

        record = self.execute_one('''
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Record_Is_In_Use, Record_Used_Counter from Records where Record_Id='''+ str(record_id) +'''
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
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Record_Is_In_Use, Record_Used_Counter from Records
            ''')
        return records

    def PrintAllRecords(self):
        records=self.ReturnAllRecords()
        for record_id in range(len(records)):
            id, name, visible, hidden, is_in_use, used_counter = records[record_id]
            print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")

    def ReturnBox(self, box_id):
        # output is list of elements
        # correct way to unpack - see ReturnAllRecords

        Box_Records = self.execute_one('''
            select Record_Id, Record_Name, Record_Visible, Record_Hidden, Record_Is_In_Use, Record_Used_Counter from Records where Record_Id in (SELECT Record_Id from Box''' + str(box_id) +''')
            ''')
        return Box_Records

    def PrintBox(self, box_id):
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
        pass

    def PrintAllBoxes(self):
        output = self.execute_one('''select Box_Id from BoxQueue''')
        Boxes_Ids = np.squeeze(output)
        print(Boxes_Ids)
        for Box_Id in Boxes_Ids:
            self.PrintBox(Box_Id)
        
        


    def AssignNext(self):
        #random function - search for record that is not in boxes already
        pass

    def EoD_Rotation(self):
        #self.AssignNext()
        # moving between boxes function
        pass


    def __init__(self, num_of_boxes=7):
        self.num_of_boxes = num_of_boxes
        self.init_db()


if __name__ == '__main__':
    db = SpacedRepetition()
    db.AddRecord("Oumi Janta", "If I can see you grove -- if you have fun -- I can see that you trully feel the music and feel the track -- And that makes you move much more beautiful", "")

    db.AddRecord("Microjournaling", "", "")

    db.AddRecord("alluring", "alluring", "atrakcyjny")

    db.AssignRecord(1, 1)
    db.AssignRecord(2, 1)


    #db.PrintBox(1)

    db.PrintAllBoxes()









