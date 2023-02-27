from __future__ import annotations
from typing import TYPE_CHECKING

import threading
import gzip
from lxml import etree
import os
import hashlib
import datetime
import shutil
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
        self.cancel_backup.set()
        self.backup_in_progress = False
        self.controller.startpage.hide_backup_frame()
        self.controller.event_generate("<<BackupIdle>>")

    def start_backup(self):
        self.cancel_backup.clear()
        self.controller.startpage.set_progress_count(0)
        self.backup_in_progress = True
        self.controller.startpage.show_backup_frame()
        self.backup_thread = threading.Thread(
            target=self.start_backup_thread,
            args=(
                self.controller.app_settings.app_settings,
                self.controller.message_queue,
                self.controller.selected_playthrough
            )
        )
        self.controller.event_generate("<<BackupRunning>>")
        self.backup_thread.start()
    
    def start_backup_thread(self, settings, message_queue, playthrough):
        from modules.app import Model
        db = Model(self.controller, settings["APP"]['DBPATH'])

        backup_path = settings["APP"]["BACKUPPATH"]
        x4_save_path = settings["APP"]["X4SAVEPATH"]
        save_seconds = settings["APP"]["BACKUPFREQUENCY_SECONDS"]
        temp_dir = os.path.join(
            backup_path, 'temp'
        )
        
        # make sure that we have a temp dir, and it's empty
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        for file in os.scandir(temp_dir):
            if '.xml' in file.name:
                os.remove(file.path)

        # create our data dictionary that we return through the messaging queue
        # and enter the main backup loop
        data = {}
        data['loops'] = 0
        data['x4saves'] = []
        while True:
            countdown = save_seconds
            data['processing'] = 0
            # sleep while we wait for the next loop
            while countdown  >= 0:
                self.controller.event_generate("<<UpdateBackupProgress>>")
                data['countdown'] = countdown
                countdown -= 1
                message_queue.put(data)
                self.controller.event_generate("<<NewQueueData>>")

                sleep(1)
                if self.cancel_backup.is_set():
                    break

            # make sure we aren't canceled before continuing
            if self.cancel_backup.is_set():
                break
            
            # get the now time
            now = datetime.datetime.now()

            # check to see if we have any x4saves that haven't been backed up
            # first - we get a list of all save files
            # second - we get the hashes for each save file
            #          and then check the DB for that hash
            # third - if the hash/file hasn't been backed up, back it up

            for file in os.scandir(x4_save_path):
                if not file.is_file() or 'xml.gz' not in file.name:
                    break

                sha256 = hashlib.sha256()
                with open(file.path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        sha256.update(chunk)
                hash = sha256.hexdigest()
                
                if db.check_backup_exists(hash):
                    break

                # file has not been backed up
                backup_filename = "id{}_{}.xml.gz".format(
                        playthrough['id'],
                        now.strftime("%Y%m%d-%H%M%S")
                )
                backup_fullpath = os.path.join(
                    backup_path,
                    backup_filename
                )
                data['x4saves'].append({
                    'x4save': file.name,
                    'backup_filename': backup_filename
                })
                x4save_time = os.path.getctime(file.path)
                try:
                    data['processing'] = 1
                    message_queue.put(data)
                    self.controller.event_generate("<<NewQueueData>>")
                    shutil.copyfile(file.path, backup_fullpath)
                    tempfilepath = os.path.join(
                        temp_dir,
                        f'{now.strftime("%Y%m%d-%H%M%S")}.xml'
                    )
                    # extract the xml in chunks so we don't kill memory
                    with gzip.open(backup_fullpath, 'rb') as f_in:
                        with open(tempfilepath, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out, 4096)
                    
                    #search the xml in a memory friendly way
                    context = etree.iterparse(
                        tempfilepath,
                        tag=('game','player','patches')
                    )
                    game_version = ''
                    original_version = ''
                    modified = ''
                    gametime = ''
                    start_type = ''
                    playername = ''
                    money = ''

                    for event, element in context:
                        if element.tag == 'game':
                            game_version = "{} build {}".format(
                                element.attrib['version'],
                                element.attrib['build']
                            )
                            original_version = "{} build {}".format(
                                element.attrib['original'],
                                element.attrib['originalbuild']
                            )
                            modified = element.attrib['modified']
                            gametime = element.attrib['time']
                            start_type = element.attrib['start']

                        if element.tag == 'player':
                            playername = element.attrib['name']
                            money = element.attrib['money']

                        # we don't need to parse the entire file
                        # stop when we complete the patches tag
                        if element.tag == 'patches':
                            break

                        element.clear()

                        # just in case we need to read past patches
                        # almost everything is in the universe, so
                        # that element will get stored in RAM
                        # this flushes it at the end
                        # kept for historical purposes
                        while element.getprevious() is not None:
                            del element.getparent()[0]
                    
                    del context
                    
                    db.add_backup(
                        playthrough['id'],
                        file.name,
                        x4save_time,
                        hash,
                        now.timestamp(),
                        backup_filename,
                        game_version,
                        original_version,
                        gametime,
                        start_type,
                        playername,
                        money,
                        modified
                    )
                except Exception as e:
                    raise e
            
            # done with this loop, get ready for the next
            data['loops'] += 1
    
