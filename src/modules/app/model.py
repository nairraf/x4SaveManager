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

    def save_playthrough(self, name, notes='', id=None, show_error=True, overwrite=False):
        # we don't use the SQLite REPLACE statement as that performs a DELETTE
        # followed by a new insert, which creates a new ID for the same name
        # we need the ID to join with the backups table, so the ID needs to 
        # stay the same across saves/updates
        insert_query="""
            INSERT INTO playthroughs (name, notes)
            VALUES (?, ?)
        """

        update_query="""
            UPDATE playthroughs SET name = ?, notes = ?
            WHERE id = ?
        """

        # see if an entry exists for this playthrough name
        cur_playthroughs = self.get_playthrough_names()
        entry = None
        if id:
            entry = self.get_playthrough_by_id(id)
        if name in cur_playthroughs:
            entry = self.get_playthrough_by_name(name)
            if not id:
                id = entry['id']
            if overwrite == False:
                return False

        with self.connection as c:
            try:
                if entry:
                    c.execute(
                        update_query,
                        (name, notes, id)
                    )
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
                file_hash
            FROM backups
            WHERE file_hash = ?
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
                , x4_filename
                , x4_save_time
                , file_hash
                , x4slot
                , backup_time
                , backup_filename
                , character_name
                , company_name
                , money
                , moded
            FROM backups
            WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: {
                    'playthrough_id': row[0],
                    'x4_filename': row[1],
                    'x4_save_time': row[2],
                    'file_hash': row[3],
                    'x4slot': row[4],
                    'backup_time': row[5],
                    'backup_filename': row[6],
                    'character_name': row[7],
                    'company_name': row[8],
                    'money': row[9],
                    'moded': row[10]
                }
                res = c.execute(query, (hash, )).fetchone()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return None

    def add_backup(
            self,
            playthrough_id,
            x4_filename,
            x4_save_time,
            file_hash,
            backup_time,
            backup_filename,
            game_version,
            original_game_version,
            playtime,
            x4_start_type,
            character_name,
            money,
            moded,
            company_name = ''
    ):
        query = """
        INSERT INTO backups (
            playthrough_id,
            x4_filename,
            x4_save_time,
            file_hash,
            backup_time,
            backup_filename,
            game_version,
            original_game_version,
            playtime,
            x4_start_type,
            character_name,
            company_name,
            money,
            moded
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """
        try:
            with self.connection as c:
                c.execute(query,(
                    playthrough_id,
                    x4_filename,
                    x4_save_time,
                    file_hash,
                    backup_time,
                    backup_filename,
                    game_version,
                    original_game_version,
                    playtime,
                    x4_start_type,
                    character_name,
                    company_name,
                    money,
                    moded
                ))
        except sqlite3.Error as e:
            self.controller.show_error(e)
    
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
                    x4_filename TEXT,
                    x4_save_time TEXT,
                    file_hash TEXT,
                    backup_time TEXT,
                    backup_filename TEXT,
                    game_version TEXT,
                    original_game_version TEXT,
                    playtime TEXT,
                    x4_start_type TEXT,
                    character_name TEXT,
                    company_name TEXT,
                    money TEXT,
                    moded BOOL
            );"""
            try:
                with self.connection as c:
                    c.execute(playthroughs_ddl)
                    c.execute(backups_ddl)
                    c.execute("PRAGMA user_version=1")
                self.get_db_version()
            except sqlite3.Error as e:
                self.controller.show_error(e)