from __future__ import annotations
from typing import TYPE_CHECKING

import sqlite3
from time import ctime

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
            self.connection = sqlite3.connect(
                self.dbpath
            )
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
                    c.commit()
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
    
    def update_backup_options(self, flag, notes, hash):
        query = """
            UPDATE backups SET flag = ?, notes = ?
            WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.execute(query, (
                    flag,
                    notes,
                    hash, 
                ))
                c.commit()
            except sqlite3.Error as e:
                self.controller.show_error(e)

    def get_backup_by_hash(self, hash):
        query = """
            SELECT
                playthrough_id
                , x4_filename
                , x4_save_time
                , file_hash
                , backup_time
                , backup_filename
                , backup_duration
                , game_version
                , original_game_version
                , playtime
                , x4_start_type
                , character_name
                , company_name
                , money
                , moded
                , flag
                , notes
            FROM backups
            WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: {
                    'playthrough_id': row[0],
                    'x4_filename': row[1],
                    'x4_save_time': ctime(row[2]),
                    'file_hash': row[3],
                    'backup_time': ctime(row[4]),
                    'backup_filename': row[5],
                    'backup_duration': row[6],
                    'game_version': row[7],
                    'original_game_version': row[8],
                    'playtime': row[9],
                    'x4_start_type': row[10],
                    'character_name': row[11],
                    'company_name': row[12],
                    'money': row[13],
                    'moded': bool(row[14]),
                    'flag': bool(row[15]),
                    'notes': row[16]
                }
                res = c.execute(query, (hash, )).fetchone()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return None
    
    def get_backups_by_id(self, playthrough_id):
        query = """
            SELECT
                playthrough_id
                , x4_filename
                , x4_save_time
                , file_hash
                , backup_time
                , backup_filename
                , backup_duration
                , game_version
                , original_game_version
                , playtime
                , x4_start_type
                , character_name
                , company_name
                , money
                , moded
                , flag
                , notes
            FROM backups
            WHERE playthrough_id = ?
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: {
                    'playthrough_id': row[0],
                    'x4_filename': row[1],
                    'x4_save_time': ctime(row[2]),
                    'file_hash': row[3],
                    'backup_time': ctime(row[4]),
                    'backup_filename': row[5],
                    'backup_duration': row[6],
                    'game_version': row[7],
                    'original_game_version': row[8],
                    'playtime': row[9],
                    'x4_start_type': row[10],
                    'character_name': row[11],
                    'company_name': row[12],
                    'money': row[13],
                    'moded': bool(row[14]),
                    'flag': bool(row[15]),
                    'notes': row[16]
                }
                res = c.execute(query, (playthrough_id, )).fetchall()
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
            backup_duration = None,
            company_name = '',
            flag = False,
            notes = ''
    ):
        query = """
        INSERT INTO backups (
            playthrough_id,
            x4_filename,
            x4_save_time,
            file_hash,
            backup_time,
            backup_filename,
            backup_duration,
            game_version,
            original_game_version,
            playtime,
            x4_start_type,
            character_name,
            company_name,
            money,
            moded,
            flag,
            notes
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
                    backup_duration,
                    game_version,
                    original_game_version,
                    playtime,
                    x4_start_type,
                    character_name,
                    company_name,
                    money,
                    moded,
                    flag,
                    notes
                ))
                c.commit()
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
                    x4_save_time TIMESTAMP,
                    file_hash TEXT NOT NULL UNIQUE,
                    backup_time TIMESTAMP,
                    backup_filename TEXT,
                    backup_duration NUMERIC,
                    game_version TEXT,
                    original_game_version TEXT,
                    playtime NUMERIC,
                    x4_start_type TEXT,
                    character_name TEXT,
                    company_name TEXT,
                    money NUMERIC,
                    moded BOOL,
                    flag BOOL,
                    notes TEXT
            );"""
            try:
                with self.connection as c:
                    c.execute(playthroughs_ddl)
                    c.execute(backups_ddl)
                    c.execute("PRAGMA user_version=1")
                    c.commit()
                self.get_db_version()
            except sqlite3.Error as e:
                self.controller.show_error(e)