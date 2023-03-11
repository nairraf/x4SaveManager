"""AppSettings Class

Handles all application settings logic, 
reading and writing to/from the JSON file 
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import json
import appdirs as appdirs
import userpaths as userpaths
from os import path, makedirs, listdir

if TYPE_CHECKING:
    from modules.gui import WindowController

class AppSettings():
    """The main AppSettings Class
    """
    def __init__(self, controller: WindowController):
        """Constructor
        
        Args:
            controller (WindowController): the main application controller
        """
        self.controller = controller
        self.config_dir = appdirs.user_config_dir(
            "x4SaveManager", False, "Release"
        )
        self.backup_dir = path.join(
            appdirs.user_data_dir(
                "x4SaveManager", False, "Release"
            ),
            "Backups"
        )
        self.config_file = path.join(self.config_dir, "config.json")
        self.app_settings = None
        self.load_config()
        self.migrations()
        
    def create_config(self):
        """Creates a new default configuration if the user configuration
        json file is not found
        """
        if not path.exists(self.config_dir):
            makedirs(self.config_dir)
        if not path.exists(self.backup_dir):
            makedirs(self.backup_dir)
        self.app_settings = {
            "APP": {
                "DBPATH": "{}".format(
                    path.join(
                        self.config_dir,
                        "x4SaveManager.db"
                    )
                ),
                "BACKUPPATH": "{}".format(self.backup_dir),
                "X4SAVEPATH": "{}".format(self.get_x4_save_path()),
                "VERSION": 2
            },
            "BACKUP": {
                "BACKUPFREQUENCY_SECONDS": 300,
                "BACKUP_PRUNING": False,
                "DELETE_QUICKSAVES": False,
                "DELETE_AUTOSAVES": False,
                "DELETE_SAVES": False,
                "DELETE_OLD_DAYS": 30,
            }
        }
        self.save()
    
    def get_x4_save_path(self):
        """Returns the path to the egosoft default X4 save location
        on windows this is c:\<user>\Documents\Egosoft\X4\#####\save"""
        try:
            mydocs = userpaths.get_my_documents()
            x4root = path.join(mydocs,'Egosoft', 'X4')
            x4savepath = None
            if x4root:
                for name in listdir(x4root):
                    if 'save' in listdir(path.join(x4root, name)):
                        x4savepath = path.join(x4root, name, 'save')
        except Exception as e:
            self.controller.show_error(e)
        
        return x4savepath

    def save(self):
        """Write the application settings to the JSON file
        """
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.app_settings, f)
            return True
        except:
            return False

    def load_config(self):
        """open the json file and reads in the application settings
        """
        try:
            with open(self.config_file, 'r') as f:
                self.app_settings = json.load(f)
        except FileNotFoundError:
            self.create_config()

    def get_app_setting(self, name, category="APP"):
        """returns the specified appsetting from the main app_settings dictionary

        Args:
            name (string): the name of the appsetting to retrieve
            category (string): the app setting category (default = "APP")
        """
        if name in self.app_settings[category]:
            return self.app_settings[category][name]
        
        return None
    
    def update_app_setting(self, name, data, category="APP"):
        """Updates the specified app setting with new data
        
        Args:
            name (string): the name of the app setting up update
            data: the new data for the app setting
            category (string): the app setting category (default = "APP")
        """
        if name in self.app_settings[category]:
            self.app_settings[category][name] = data
            return True
        
        return False
    
    def _create_app_setting(self, name, data, category):
        """creates and app setting and category if needed
        
        Args:
            name (string): the name of the setting
            data (string): the data/value to associate with the setting
            category (string): the category the setting should be placed in
        """
        if not category in self.app_settings:
            self.app_settings[category] = {}
        self.app_settings[category][name] = data

    def _delete_app_setting(self, name, category):
        """deletes and app setting
        
        Args:
            name (string): the name of the setting to delete
            category (string): the category that the setting is associated with
        """
        if name in self.app_settings[category]:
            del self.app_settings[category][name]

    def migrations(self):
        """Responsible for updating the app settings between versions
        """

        if self.get_app_setting("VERSION") == 1:
            self.update_app_setting("VERSION", 2)
            # move the backup frequency setting to the backup category
            self._create_app_setting(
                "BACKUPFREQUENCY_SECONDS",
                self.get_app_setting("BACKUPFREQUENCY_SECONDS"),
                category="BACKUP"
            )
            self._delete_app_setting(
                "BACKUPFREQUENCY_SECONDS",
                category="APP"
            )
            # add more backup settings to the backup category
            self._create_app_setting(
                "BACKUP_PRUNING",
                False,
                category="BACKUP"
            )
            self._create_app_setting(
                "DELETE_QUICKSAVES",
                False,
                category="BACKUP"
            )
            self._create_app_setting(
                "DELETE_AUTOSAVES",
                False,
                category="BACKUP"
            )
            self._create_app_setting(
                "DELETE_SAVES",
                False,
                category="BACKUP"
            )
            self._create_app_setting(
                "DELETE_OLD_DAYS",
                30,
                category="BACKUP"
            )
            self.save()
        