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

    def delete_playthrough(self):
        """Deletes the currently selected playthrough
        """
        if self.controller.selected_playthrough:
            self.controller.show_question(
                "Are you sure you want to delete Playthrough:\n{}".format(
                    self.controller.selected_playthrough["name"]
                )
            )
            
            if not self.controller.check_modal():
                return

            backups = self.controller.db.get_backups_by_id(
                self.controller.selected_playthrough["id"]
            )

            for backup in backups:
                self.controller.db.backup_set_delete(
                    backup["file_hash"],
                    move_playthrough = True
                )

            if self.controller.db.delete_playthrough_by_name(
                self.controller.selected_playthrough["name"]
            ):
                self.controller.show_message(
                    "Playthrough {} has been marked for deletion".format(
                        self.controller.selected_playthrough["name"]
                    )
                )
                self.controller.selected_playthrough = None
                self.controller.startpage.refresh_playthroughs()
                self.controller.startpage.playthroughs.selection_clear(0)
                self.controller.statusbar.set_playthrough("None")
                self.controller.top_menu.menu_backup.entryconfigure(
                    'Start Backup',
                    state='disabled'
                )
                self.controller.startpage.set_notes("")

