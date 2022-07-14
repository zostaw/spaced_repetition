# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 12:00:00 2022

@author: zostaw
"""

import os
import sqlite3


class SpacedRepetition():

    # database class - it serves to store and manage elements (facts/quotse) and provides 
    # querries to shufle them, add, manage the daily boxes

    spaced_rep_db = 'spaced_rep_db'

    def execute(self, querry, db=spaced_rep_db):
        conn = sqlite3.connect(db)
        c = conn.cursor()
        result = c.execute(querry)
        conn.commit()
        
        return list(result)

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

        for num in range(self.num_of_boxes):
            c.execute('''
                CREATE TABLE IF NOT EXISTS Box''' + str(num) + '''
                (
                [Box_Record_Id] INTEGER PRIMARY KEY, 
                [Box_Record] INTEGER,
                FOREIGN KEY(Box_Record) REFERENCES Records(Record_Id)
                )
                ''')
        conn.commit()

    def AddRecord(self, name, visible_text="", hidden_text=""):
        self.execute('''
            INSERT INTO Records
            (Record_Name, Record_Visible, Record_Hidden)
            VALUES ("''' + name + '''",
            "''' + visible_text + '''",
            "''' + hidden_text + '''")
            ''')

    def AssignRecord(self, element_id, box_id=0):
        self.execute('''
            INSERT INTO Box''' + str(box_id) + '''
            ([Box_Record])
            VALUES (''' + element_id + ''')
            ''')



    
    def RemoveRecord(self):
        pass

    def PrintRecord(self, record_id):
        # output is list of elements
        # correct way to unpack:
        # id, name, visible, hidden, is_in_use, used_counter = db.PrintRecord(id)

        record_columns=["Record_Id", "Record_Name", "Record_Visible", "Record_Hidden", "Record_Is_In_Use", "Record_Used_Counter"]

        record = { }
        for column in record_columns:
            record[column] = self.execute('''
                select '''+ str(column) +''' from Records where Record_Id='''+ str(record_id) +'''
                ''')
        return record.values()

    def PrintAllRecords(self):
        # output is list of lists (for each column)
        # correct way to unpack:
        # id, name, visible, hidden, is_in_use, used_counter = db.PrintAllRecords()

        record_columns=["Record_Id", "Record_Name", "Record_Visible", "Record_Hidden", "Record_Is_In_Use", "Record_Used_Counter"]

        record = { }
        for column in record_columns:
            record[column] = self.execute('''
                select '''+ str(column) +''' from Records
                ''')
        return record.values()


    def PrintAll(self):
        return list(self.execute('''select * from Records'''))

    def __init__(self, num_of_boxes=7):
        self.num_of_boxes = num_of_boxes
        self.init_db()


if __name__ == '__main__':
    db = SpacedRepetition()
    db.AddRecord("Oumi Janta", "If I can see you grove -- if you have fun -- I can see that you trully feel the music and feel the track -- And that makes you move much more beautiful", "")
    id, name, visible, hidden, is_in_use, used_counter = db.PrintAllRecords()
    print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")

    [id, name, visible, hidden, is_in_use, used_counter] = db.PrintRecord(1)
    print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")
