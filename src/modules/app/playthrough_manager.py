"""Holds the PlaythroughManager class

PlaythroughManager is responsible for managing playthrough actions
"""
from __future__ import annotations
from typing import TYPE_CHECKING

import os
import shutil
import re

if TYPE_CHECKING:
    from modules.gui import WindowController

class PlaythroughManager():
    """PlaythroughManager Class
    """
    def __init__(self, controller: WindowController):
        """Manages playthroughs

        Args:
            controller (WindowController): the root TK controller
        """
        self.controller = controller
        self.backup_root = self.controller.app_settings.get_app_setting('BACKUPPATH')

    def move_backups_to_index(self, backups, playthrough_id):
        """moves backups to the specified playthrough
        
        Args:
            backups (list): list of dictionaries in the form of:
                            [{'filename': '', 'hash':''}]
                            each dictionary element will target the backup with
                            the specified hash and current filename
            playthrough_id (int): the id of the playthrough that the backup list
                                  will be associated with
        """                
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

