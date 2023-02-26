from __future__ import annotations
from typing import TYPE_CHECKING

import threading
from time import sleep
if TYPE_CHECKING:
    from modules.gui import WindowController

class SaveManager():
    def __init__(self, controller: WindowController):
        """Manages the backup save process

        Args:
            controller (WindowController): the root TK controller
        """
        self.controller = controller
        self.backup_thread = None
        self.backup_in_progress = False
        self.cancel_backup = threading.Event()

    def stop_backup(self):
        if not self.backup_in_progress:
            self.controller.show_error("No backup in progress..")
            return
        
        self.cancel_backup.set()
        self.backup_in_progress = False
        self.controller.startpage.hide_backup_frame()

    def start_backup(self):
        if self.backup_in_progress:
            self.controller.show_error("Backup already in progress..")
            return
        
        self.cancel_backup.clear()
        self.controller.startpage.set_progress_count(0)
        self.backup_in_progress = True
        self.controller.startpage.show_backup_frame()
        self.backup_thread = threading.Thread(
            target=self.start_backup_thread
        )
        self.backup_thread.start()
    
    def start_backup_thread(self):
        while True:
            sleep(1)
            if self.cancel_backup.is_set():
                break
            self.controller.event_generate("<<UpdateBackupProgress>>")
    
