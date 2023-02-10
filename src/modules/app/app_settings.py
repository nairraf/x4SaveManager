import json
from os import path, makedirs
import appdirs as appdirs

class AppSettings():
    def __init__(self, controller):
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
        
    def create_config(self):
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
                "BACKUPPATH": "{}".format(self.backup_dir)
            }
        }
        self.save()

    def save(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.app_settings, f)
            return True
        except:
            return False

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.app_settings = json.load(f)
        except FileNotFoundError:
            self.create_config()

    def get_app_setting(self, name):
        return self.app_settings["APP"][name]
    
    def update_app_setting(self, name, data):
        self.app_settings["APP"][name] = data

    

        