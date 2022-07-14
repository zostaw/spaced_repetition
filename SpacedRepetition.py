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

    def init_db(self):
        #initiate database
        conn = sqlite3.connect('spaced_rep_db')
        c = conn.cursor()
    
        c.execute('''
            CREATE TABLE IF NOT EXISTS Elements
            (
            [Element_Id] INTEGER PRIMARY KEY, 
            [Element_Name] TEXT NOT NULL, 
            [Element_Visible] TEXT DEFAULT "", 
            [Element_Hidden] TEXT DEFAULT "", 
            [Element_Is_In_Use] BOOLEAN DEFAULT 0, 
            [Element_Used_Counter] INTEGER DEFAULT 0
            )
            ''')
        conn.commit()


    def __init__(self):
        self.init_db()


if __name__ == '__main__':
    db = SpacedRepetition()
    #run()
