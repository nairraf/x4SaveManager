"""Holds the Model Class

Responsible for all SQLite database read/writes for the application
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import sqlite3
from time import ctime

if TYPE_CHECKING:
    from modules.gui import WindowController

class Model():
    """The Model Class
    handles all database logic/io
    """
    def __init__(self, controller: WindowController, dbpath: str):
        """constructor
        
        Args:
            controller (WindowController): the main application controller
            dbpath (string): the full path to the application SQLite database
        """
        self.dbpath = dbpath
        self.controller = controller
        self.connection = None
        self.version = None
        self._connect()
        
    def _connect(self):
        """Connects to the SQLite Application database
        """
        try:
            self.connection = sqlite3.connect(
                self.dbpath
            )
            self.get_db_version()
            self.migrations()
        except sqlite3.Error as e:
            self.controller.show_error(e)
    
    def get_db_version(self):
        """Retrieves the SQLite user_version
        
        User to track schema version and which migrations are needed
        across application updates
        """
        try:
            self.version, = self.connection.execute(
                "PRAGMA user_version").fetchone()
        except sqlite3.Error as e:
            self.controller.show_error(e)

    def save_playthrough(self, name, notes='', id=None, show_error=True, overwrite=False):
        """Saves/Updates a new playthrough to the playthroughs table

        Args:
            name (string): the name of the playthrough
            notes (string): the notes for the playthrough
            id (int): specify an ID to update an existing playthrough
            show_error (bool): default True to show application level errors
            overwrite (bool): default False. does not allow overwriting a 
                              playthrough by default. Specify True to overwrite.
        """
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
            except sqlite3.IntegrityError as e:
                if show_error:
                    self.controller.show_error("""That playthrough name already exists.
Please choose a different playthrough name, one that doesn't already exist.""")
            except sqlite3.Error as e:
                if show_error:
                    self.controller.show_error(e)
        
        return False

    def delete_playthrough_by_name(self, name):
        """Deletes a playthrough from the playthroughs table
        
        Args:
            name (str): the name of the playthrough to delete
        """
        query="""
        DELETE FROM playthroughs 
        WHERE name = ?
        """
        
        # we don't delete the __RECYCLE BIN__ playthrough
        if name == "__RECYCLE BIN__":
            return False
        
        with self.connection as c:
            try:
                c.execute(query,(name,))
                return True
            except sqlite3.Error as e:
                    self.controller.show_error(e)
        
        return False

    def get_playthrough_by_id(self, id):
        """retrieve the playthrough with a specific id

        Args:
            id (int): the id of the playthrough to retreive
        """
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
        """retrieve the playthrough with a specific name

        Args:
            name (str): the name of the playthrough to retreive
        """
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

    def get_playthroughs(self):
        """get all playthroughs
        """
        query="""
        SELECT id, name, notes FROM playthroughs
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: {
                    "id": row[0],
                    "name": row[1],
                    "notes": row[2]
                }
                res = c.execute(query).fetchall()
                return res 
            except sqlite3.Error as e:
                self.controller.show_error(e)
                
    def get_playthrough_names(self):
        """get only the names of the playthroughs
        
        used by widgets when just the names are needed
        """
        query = """
            SELECT name FROM playthroughs
            ORDER BY CASE WHEN name = '__RECYCLE BIN__' THEN 1 else 2 END, name COLLATE NOCASE ASC
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: row[0]
                res = c.execute(query).fetchall()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)

    def check_backup_exists(self, hash):
        """a test to see if a backup exists for a certain file hash

        Args:
            hash (str): the SHA256 file hash to lookup
        """
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
    
    def save_backup(self, playthrough_id, branch, flag, notes, delete, file_hash):
        """Used by the edit backup window. Saves the changes for
        the specific file_hash to the DB.

        Args:
            playthrough_id (int): the corresponding playthrough id
            branch (str): the branch to assign the backup to
            flag (bool): flag this backup
            notes (str): the notes for this backup
            delete (bool): the delete flag for this backup
            file_hash (str): the hash of the backup to update
        """
        query = """
            UPDATE backups 
            SET playthrough_id = ?, branch = ?, flag = ?, notes = ?, "delete" = ?
            WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.execute(query, (
                    playthrough_id,
                    branch,
                    flag,
                    notes,
                    delete,
                    file_hash,
                ))
                c.commit()
                return True
            except sqlite3.Error as e:
                self.controller.show_error(e)

        return False
    
    def backup_set_delete(self, hash, move_playthrough=False):
        """marks a backup for deletion

        Args:
            hash (str): the hash for the backup to mark for deletion
            move_playthrough (bool): default False. If True then
                the playthrough is moved to the __RECYCLE BIN__ playthrough
        """
        query = """
                UPDATE backups SET "delete" = TRUE
                WHERE file_hash = ?
            """
        if move_playthrough:
            query = """
                UPDATE backups SET "delete" = TRUE, playthrough_id = ?
                WHERE file_hash = ?
            """
            # figure out the playthrough_id for __DELEDTED__ playthrough
            dp = self.get_playthrough_by_name("__RECYCLE BIN__")
        
        with self.connection as c:
            try:
                if move_playthrough:
                    c.execute(query, (
                        dp['id'],
                        hash
                    ))
                else:
                    c.execute(query, (
                        hash,
                    ))
                c.commit()
                return True
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return False
    
    def backup_unset_delete(self, hash):
        """unmarks a backup for deletion. The playthrough must not be set to
        the __RECYCLE BIN__ playthrough

        Args:
            hash (str): the hash for the backup to mark for deletion
        """
        query = """
            UPDATE backups SET "delete" = FALSE
            WHERE file_hash = ?
        """
        # figure out the playthrough_id for __DELEDTED__ playthrough
        dp = self.get_playthrough_by_name("__RECYCLE BIN__")
        backup = self.get_backup_by_hash(hash)

        if not dp['id'] == backup['playthrough_id']:
            with self.connection as c:
                try:
                    c.execute(query, (
                        hash,
                    ))
                    c.commit()
                    return True
                except sqlite3.Error as e:
                    self.controller.show_error(e)
        else:
            self.controller.show_error("""Cannot Undelete backup {}.
Please move the playthrough out of the __RECYCLE BIN__ 
by assigning it to another playthrough""".format(
            backup['backup_filename']
            ))
        
        return False

    def update_backup_options(self, flag, notes, branch, hash):
        """updates just the flag and notes fields for a specific
        backup specified be the file hash

        Args:
            flag (bool): sets the flag for this backup
            notes (str): the notes for this backup
            branch (str): the branch for this backup
            hash (str): the SHA256 hash of the backup to update
        """
        query = """
            UPDATE backups SET flag = ?, notes = ?, branch = ?
            WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.execute(query, (
                    flag,
                    notes,
                    branch,
                    hash, 
                ))
                c.commit()
            except sqlite3.Error as e:
                self.controller.show_error(e)

    def update_backup_flag(self, flag, hash):
        """updates just the flag and notes fields for a specific
        backup specified be the file hash

        Args:
            flag (bool): sets the flag for this backup
            hash (str): the SHA256 hash of the backup to update
        """
        query = """
            UPDATE backups SET flag = ?
            WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.execute(query, (
                    flag,
                    hash, 
                ))
                c.commit()
            except sqlite3.Error as e:
                self.controller.show_error(e)

    def get_branches(self, playthrough_id):
        """returns a list of branches associated for the given playthrough id

        Args:
            playthrough_id (int): the playthrough id
        """
        query="""
            SELECT DISTINCT(branch) FROM backups
            WHERE playthrough_id = ?
            ORDER BY branch 
        """
        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: row[0]
                res = c.execute(query, (playthrough_id, )).fetchall()
                if res:
                    return res
                else:
                    return ['1 - main']
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return None

    def set_branch(self, hash, branch):
        """updates the branch name for a specific playthrough matched 
        by the file hash

        Args:
            hash (str): the file hash
            branch (str): the branch name
        """
        query = """
            UPDATE backups SET branch = ?
            WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.execute(query, (
                    branch,
                    hash, 
                ))
                c.commit()
            except sqlite3.Error as e:
                self.controller.show_error(e)

    def update_backup_playthrough(self, playthrough_id, backup_filename, hash):
        """updates the playthrough_id and the backup_filename for a specific
        backup specified by hash. Used when moving a backup between playthroughs
        
        Args:
            playthrough_id (int): the playthrough ID to associate this backup with
            backup_filename (str): the name of the backup file
            hash (str): the hash of record which will be updated
        """
        query = """
            UPDATE backups SET playthrough_id = ?, backup_filename = ?
            WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.execute(query, (
                    playthrough_id,
                    backup_filename,
                    hash, 
                ))
                c.commit()
            except sqlite3.Error as e:
                self.controller.show_error(e)

    def get_backup_by_hash(self, hash):
        """Gets a specific backup specified by the hash
        
        Args:
            hash (str): the backup with this hash to retrieve
        """
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
                , "delete"
                , branch
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
                    'money': float(row[13] if row[13] else 0),
                    'moded': bool(row[14]),
                    'flag': bool(row[15]),
                    'notes': row[16],
                    'delete': bool(row[17]),
                    'branch': row[18]
                }
                res = c.execute(query, (hash, )).fetchone()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return None
    
    def delete_backup(self, hash):
        """Deletes a specific backup from the backups table
        
        Args:
            hash (str): the file_hash of the backup to delete
        """
        query = """
            DELETE FROM backups WHERE file_hash = ?
        """
        with self.connection as c:
            try:
                c.execute(query, (
                    hash, 
                ))
                c.commit()
            except sqlite3.Error as e:
                self.controller.show_error(e)


    def get_backups_to_delete(
            self,
            sort_column='x4_save_time',
            sort_direction='asc'
        ):
        """retreives all backups that have been marked for deletion
        """
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
                , "delete"
                , branch
            FROM backups
            WHERE "delete" = TRUE
            ORDER BY {} {}
        """.format(
            sort_column,
            sort_direction
        )

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
                    'money': float(row[13] if row[13] else 0),
                    'moded': bool(row[14]),
                    'flag': bool(row[15]),
                    'notes': row[16],
                    'delete': bool(row[17]),
                    'branch': row[18]
                }
                res = c.execute(query).fetchall()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return None

    def get_latest_backups(self):
        """returns the file_hashes of the latest backups.
        The number returned is configed in the backup options
        "Do Not Prune Last Backups" option
        """
        query = """
            SELECT file_hash FROM backups ORDER BY x4_save_time DESC LIMIT {}
        """.format(
            self.controller.app_settings.get_app_setting(
                'DO_NOT_DELETE_LAST',
                category='BACKUP'
            )
        )

        with self.connection as c:
            try:
                c.row_factory = lambda cursor, row: row[0]
                res = c.execute(query).fetchall()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return None

    def get_backups_by_id(
            self,
            playthrough_id,
            include_to_delete=False,
            sort_column='x4_save_time',
            sort_direction='asc',
            branch=None
        ):
        """retreives all backups associated with a specific playthrough
        specified by it's id
        
        Args:
            playthrough_id (str): the playthrough_id
            include_to_delete (bool): default False. Includes the items marked
                                      for deletion
            sort_column (str): which column to sort by (default is x4_save_time)
            sort_direction (str): Default Asc. Asc/Desc
            branch (str): by default all branches are returned. 
                          limits the results to a specific branch
        """
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
                , "delete"
                , branch
            FROM backups
            WHERE playthrough_id = ?
        """

        if not include_to_delete:
            query += " AND \"delete\" IS NOT TRUE"

        if not branch:
            branch = '%'

        query += " AND branch like '{}'".format(branch)

        # SQL Parameters can't be used in the order by
        # they can only be used to replace values
        query += " ORDER BY {} {}".format(
            sort_column,
            sort_direction
        )

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
                    'money': float(row[13] if row[13] else 0),
                    'moded': bool(row[14]),
                    'flag': bool(row[15]),
                    'notes': row[16],
                    'delete': bool(row[17]),
                    'branch': row[18]
                }
                res = c.execute(query, (
                    playthrough_id,
                )).fetchall()
                return res
            except sqlite3.Error as e:
                self.controller.show_error(e)
        
        return None
    
    def get_old_backups(self):
        """retreives all backups older then the 'delete_old_days' app setting
        which don't already have the delete mark set, and which don't have the
        do not delete flag set
        """
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
                , "delete"
                , branch
            FROM backups
            WHERE 
                x4_save_time <= unixepoch('now', '-{} day')
                AND NOT "delete"
                AND NOT flag
        """.format(
            self.controller.app_settings.get_app_setting(
                'DELETE_OLD_DAYS',
                category='BACKUP'
            )
        )

        if (
            self.controller.app_settings.get_app_setting(
                'DELETE_QUICKSAVES',
                category='BACKUP'
            ) == False
        ):
            query += " and x4_filename NOT LIKE 'quicksave%' "
        
        if (
            self.controller.app_settings.get_app_setting(
                'DELETE_AUTOSAVES',
                category='BACKUP'
            ) == False
        ):
            query += " and x4_filename NOT LIKE 'autosave%' "
        
        if (
            self.controller.app_settings.get_app_setting(
                'DELETE_SAVES',
                category='BACKUP'
            ) == False
        ):
            query += " and x4_filename NOT LIKE 'save%' "

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
                    'money': float(row[13] if row[13] else 0),
                    'moded': bool(row[14]),
                    'flag': bool(row[15]),
                    'notes': row[16],
                    'delete': bool(row[17]),
                    'branch': row[18]
                }
                res = c.execute(query).fetchall()
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
            notes = '',
            delete = False,
            branch = "1 - main"
    ):
        """adds a new backups to the backups table
        
        Args:
            playthrough_id (int): the ID of the playthrough for this backup
            x4_filename (str): the original name of the x4 save
            x4_save_time (timestamp): the timestamp of the x4 save file
            file_hash (str): the SHA256 of the x4 save file
            backup_time (timestamp): the timestamp of the backup file
            backup_filename (str): the name of the backup file
            game_version (str): the version of the game for this save file
            original_game_version (str): the original version of the game for this playthrough
            playtime (float): number of seconds for this playthrough so far
            x4_start_type (str): the x4 start that was chosen for this playthrough
            character_name (str): the name of the in-game character
            money (float): the amount of money the character owns
            moded (bool): were mods used for this playthrough
            backup_duration (float): how long the backup process took
            company_name (str): the characters company name
            flag (bool): the importance flag for this backup
            notes (str): the notes for this backup
            delete (bool): sets the delete flag (default: false)
            branch (str): sets the playthrough branch for this backup.
                          default: 1 - main
        """
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
            notes,
            "delete",
            branch
        )
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
                    notes,
                    delete,
                    branch
                ))
                c.commit()
        except sqlite3.Error as e:
            self.controller.show_error(e)
    
    def migrations(self):
        """Creates the DB Schema on first load and for application updates
        """
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

        if self.version == 1:
            backups_ddl = """
                ALTER TABLE backups
                ADD COLUMN "delete" BOOL;
            """
            query1 = """
                UPDATE backups set "delete" = FALSE
                WHERE "delete" IS NULL
            """
            query2 = """
                INSERT INTO playthroughs (name, notes)
                VALUES ('__RECYCLE BIN__', 'All Playthroughs with the delete flag set are listed here')
            """
            try:
                with self.connection as c:
                    c.execute(backups_ddl)
                    c.execute(query1)
                    c.execute(query2)
                    c.execute("PRAGMA user_version=2")
                    c.commit()
                self.get_db_version()
            except sqlite3.Error as e:
                self.controller.show_error(e)

        if self.version == 2:
            branch_ddl = """
                ALTER TABLE backups
                ADD COLUMN branch TEXT
            """
            query = """
                UPDATE backups SET branch = "1 - main"
            """
            try:
                with self.connection as c:
                    c.execute(branch_ddl)
                    c.execute(query)
                    c.execute("PRAGMA user_version=3")
                    c.commit()
                self.get_db_version()
            except sqlite3.Error as e:
                self.controller.show_error(e)