import sqlite3

class Model():
    def __init__(self, db):
        self.db = db
    
    def connect(self):
        self.connection = sqlite3.connect(self.db)