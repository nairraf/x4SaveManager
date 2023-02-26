from __future__ import annotations
from typing import TYPE_CHECKING

import sqlite3

if TYPE_CHECKING:
    from modules.gui import WindowController

class Model():
    def __init__(self, controller: WindowController, dbpath: str):
        self.dbpath = dbpath
        self.controller = controller
        self.connection = None
        self.version = None
        self._connect()
        
    def _connect(self):
        try:
            self.connection = sqlite3.connect(self.dbpath)
            self.get_db_version()
            self.migrations()
        except sqlite3.Error as e:
            self.controller.show_error(e)
    
    def get_db_version(self):
        try:
            self.version, = self.connection.execute(
                "PRAGMA user_version").fetchone()
        except sqlite3.Error as e:
            self.controller.show_error(e)

    def save_playthrough(self, name, notes='', show_error=True, overwrite=False):
        # we don't use the SQLite REPLACE statement as that performs a DELETTE
        # followed by a new insert, which creates a new ID for the same name
        # we need the ID to join with the backups table, so the ID needs to 
        # stay the same across saves/updates
        insert_query="""
            INSERT INTO playthroughs (name, notes)
            VALUES (?, ?)
        """

        update_query="""
            UPDATE playthroughs SET notes = ?
            WHERE name = ?
        """
       
        cur_playthroughs = self.get_playthrough_names()
        entry_exists = False
        if name in cur_playthroughs:
            entry_exists = True
            if overwrite == False:
                return False
        
        with self.connection as c:
            try:
                if entry_exists:
                    c.execute(update_query,(notes, name))
                else:
                    c.execute(insert_query,(name, notes))
                return True
            except sqlite3.Error as e:
                if show_error:
                    self.controller.show_error(e)
        
        return False

    def delete_playthrough_by_name(self, name):
        query="""
        DELETE FROM playthroughs 
        WHERE name = ?
        """
        with self.connection as c:
            try:
                c.execute(query,(name,))
                return True
            except sqlite3.Error as e:
                    self.controller.show_error(e)
        
        return False

    def get_playthrough_by_id(self, id):
        query="""
        SELECT id, name, notes FROM playthroughs
        WHERE id = ?
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: {
                    "id": row[0],
                    "name": row[1],
                    "notes": row[2]
                }
                res = c.execute(query, (id,)).fetchone()
                return res 
            except sqlite3.Error as e:
                    self.controller.show_error(e)
    
    def get_playthrough_by_name(self, name):
        query="""
        SELECT id, name, notes FROM playthroughs
        WHERE name = ?
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: {
                    "id": row[0],
                    "name": row[1],
                    "notes": row[2]
                }
                res = c.execute(query, (name,)).fetchone()
                return res 
            except sqlite3.Error as e:
                    self.controller.show_error(e)
                
    def get_playthrough_names(self):
        query = """
            SELECT name FROM playthroughs
            ORDER BY name
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: row[0]
                res = c.execute(query).fetchall()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)

    def check_backup_exists(self, hash):
        query = """
            SELECT
                original_hash
            FROM backups
            WHERE original_hash = ?
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: row[0]
                res = c.execute(query, (hash, )).fetchone()
                if res:
                    return True
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return False

    def get_backup_by_hash(self, hash):
        query = """
            SELECT
                playthrough_id
                , original_filename
                , save_time
                , original_hash
                , x4slot
                , backup_time
                , backup_filename
            FROM backups
            WHERE original_hash = ?
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: {
                    'playthrough_id': row[0],
                    'original_filename': row[1],
                    'save_time': row[2],
                    'original_hash': row[3],
                    'x4slot': row[4],
                    'backup_time': row[5],
                    'backup_filename': row[6]
                }
                res = c.execute(query, (hash, )).fetchone()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return None


    def migrations(self):
        if self.version == 0:
            playthroughs_ddl = """
                CREATE TABLE IF NOT EXISTS playthroughs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    notes TEXT
            );"""
            backups_ddl = """
                CREATE TABLE IF NOT EXISTS backups (
                    playthrough_id INTEGER NOT NULL,
                    original_filename TEXT,
                    save_time TEXT,
                    original_hash TEXT,
                    x4slot TEXT,
                    backup_time TEXT,
                    backup_filename TEXT
            );"""
            try:
                with self.connection as c:
                    c.execute(playthroughs_ddl)
                    c.execute(backups_ddl)
                    c.execute("PRAGMA user_version=1")
                self.get_db_version()
            except sqlite3.Error as e:
                self.controller.show_error(e)