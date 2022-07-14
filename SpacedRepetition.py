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
        record_name = self.execute('''
            select Record_Name from Records where Record_Id='''+ str(record_id) +'''
            ''')
        record_visible = self.execute('''
            select Record_Visible from Records where Record_Id='''+ str(record_id) +'''
            ''')
        record_hidden = self.execute('''
            select Record_Hidden from Records where Record_Id='''+ str(record_id) +'''
            ''')
        record_is_in_use = self.execute('''
            select Record_Is_In_Use from Records where Record_Id='''+ str(record_id) +'''
            ''')
        record_used_counter = self.execute('''
            select Record_Used_Counter from Records where Record_Id='''+ str(record_id) +'''
            ''')

        return record_id, record_name, record_visible, record_hidden, record_is_in_use, record_used_counter

    def PrintAllRecords(self):
        record_id = self.execute('''
            select Record_Id from Records
            ''')
        record_name = self.execute('''
            select Record_Name from Records
            ''')
        record_visible = self.execute('''
            select Record_Visible from Records
            ''')
        record_hidden = self.execute('''
            select Record_Hidden from Records
            ''')
        record_is_in_use = self.execute('''
            select Record_Is_In_Use from Records
            ''')
        record_used_counter = self.execute('''
            select Record_Used_Counter from Records
            ''')

        return list(record_id), list(record_name), list(record_visible), list(record_hidden), list(record_is_in_use), list(record_used_counter)

    def PrintAll(self):
        return list(self.execute('''select * from Records'''))

    def __init__(self, num_of_boxes=7):
        self.num_of_boxes = num_of_boxes
        self.init_db()


if __name__ == '__main__':
    db = SpacedRepetition()
    db.AddRecord("Oumi Janta", "If I can see you grove -- if you have fun -- I can see that you trully feel the music and feel the track -- And that makes you move much more beautiful", "")
    #id, name, visible, hidden, is_in_use, used_counter = db.PrintAllRecords()
    #print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")

    id, name, visible, hidden, is_in_use, used_counter = db.PrintRecord(1)
    print("id: " + str(id) + ", name: "+ str(name) + ", visible: "+ str(visible) + ", hidden: "+ str(hidden) + ", Is in use: " + str(is_in_use) + ", used counter: " + str(used_counter) + " .")
