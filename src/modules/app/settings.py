import yaml
import os as os

class Settings():
    def __init__(self, controller, approot):
        config_file= os.path.join(os.path.join(approot, "conf"), "conf2.yaml")

        try:
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            controller.show_error(
                "Config File Not found:\n{}".format(config_file),
            )
        