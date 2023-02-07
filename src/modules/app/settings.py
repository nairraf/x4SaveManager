import json
from os import path, makedirs
import appdirs as appdirs

class Settings():
    def __init__(self, controller):
        self.controller = controller
        self.config_root = appdirs.user_config_dir(
            "x4SaveManager", False, "Release"
        )
        self.config_file = path.join(self.config_root, "config.json")
        self.app_settings = None
        self.load_config()
        
    def create_config(self):
        if not path.exists(self.config_root):
            makedirs(self.config_root)
        self.app_settings = {
            "APP": {
                "DBPATH": "{}".format(
                    path.join(
                        appdirs.user_data_dir("x4SaveManager", False, "Release"),
                        "x4SaveManager.db"
                    )
                )
            }
        }
        self.save_config()

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.app_settings, f)

    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                self.app_settings = json.load(f)
        except FileNotFoundError:
            self.create_config()
    

        