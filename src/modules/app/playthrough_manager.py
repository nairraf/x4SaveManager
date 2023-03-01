from __future__ import annotations
from typing import TYPE_CHECKING

import os
import shutil
import re

if TYPE_CHECKING:
    from modules.gui import WindowController

class PlaythroughManager():
    def __init__(self, controller: WindowController):
        """Manages playthroughs

        Args:
            controller (WindowController): the root TK controller
        """
        self.controller = controller
        self.backup_root = self.controller.app_settings.get_app_setting('BACKUPPATH')

    def move_backups_to_index(self, backups, playthrough_id):
        for back in backups:
            try:
                src = os.path.join(self.backup_root, back['filename'])
                if os.path.exists(src):
                    id=playthrough_id
                    new_filename = re.sub("^id[0-9]*_", f"id{id}_", back['filename'])
                    dst = os.path.join(self.backup_root, new_filename)
                    os.rename(src, dst)
                else:
                    raise Exception("Backup File Doesn't Exist")
                
                self.controller.db.update_backup_playthrough(
                    playthrough_id,
                    new_filename,
                    back['hash']
                )
            except Exception as e:
                self.controller.show_error(e)

