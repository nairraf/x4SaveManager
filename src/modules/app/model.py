import sqlite3

class Model():
    def __init__(self, controller, dbpath):
        self.dbpath = dbpath
        self.controller = controller
        self.connection = None
        self.version = None
        self._connect()
        
    def _connect(self):
        try:
            self.connection = sqlite3.connect(self.dbpath)
            self.update_version()
            self.migrations()
        except sqlite3.Error as e:
            self.controller.show_error(e)
    
    def update_version(self):
        try:
            self.version, = self.connection.execute(
                "PRAGMA user_version").fetchone()
        except sqlite3.Error as e:
            self.controller.show_error(e)

    def add_playthrough(self, name, notes=''):
        query="""
            INSERT INTO playthroughs (name, notes)
            VALUES (?, ?)
        """
        cur_playthroughs = self.get_playthrough_names()
        if name not in cur_playthroughs:
            with self.connection as c:
                try:
                    c.execute(query,(name, notes))
                except sqlite3.Error as e:
                    self.controller.show_error(e)
        else:
          self.controller.show_error(
              f"Error adding playthough: {name}\n Playthrough already Exists."
          )

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

    def migrations(self):
        if self.version == 0:
            playthroughs_ddl = """
                CREATE TABLE IF NOT EXISTS playthroughs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    notes TEXT
            );"""
            try:
                with self.connection as c:
                    c.execute(playthroughs_ddl)
                    c.execute("PRAGMA user_version=1")
                self.update_version()
            except sqlite3.Error as e:
                self.controller.show_error(e)